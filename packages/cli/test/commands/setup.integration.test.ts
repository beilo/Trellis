/**
 * Integration tests for the setup() command.
 *
 * Tests setup target dispatch in real temp directories while mocking external
 * child processes.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

vi.mock("node:child_process", () => ({
  execSync: vi.fn().mockReturnValue(""),
}));

import { setup } from "../../src/commands/setup.js";
import { DIR_NAMES } from "../../src/constants/paths.js";
import { execSync } from "node:child_process";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const noop = () => {};
const GITNEXUS_SETUP_COMMAND = "npx --yes gitnexus setup";

describe("setup() integration", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "trellis-setup-int-"));
    vi.spyOn(process, "cwd").mockReturnValue(tmpDir);
    vi.spyOn(console, "log").mockImplementation(noop);
    vi.mocked(execSync).mockClear();
    vi.mocked(execSync).mockReturnValue("");
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("#1 runs GitNexus setup inside an initialized Trellis project", () => {
    fs.mkdirSync(path.join(tmpDir, DIR_NAMES.WORKFLOW));

    setup("gitnexus");

    expect(execSync).toHaveBeenCalledTimes(1);
    expect(execSync).toHaveBeenCalledWith(GITNEXUS_SETUP_COMMAND, {
      cwd: tmpDir,
      stdio: "inherit",
    });
  });

  it("#2 rejects GitNexus setup outside a Trellis project", () => {
    expect(() => setup("gitnexus")).toThrow(
      'Cannot run setup outside a Trellis project. Run "trellis init" first.',
    );
    expect(execSync).not.toHaveBeenCalled();
  });

  it("#3 rejects unknown setup targets before running child processes", () => {
    fs.mkdirSync(path.join(tmpDir, DIR_NAMES.WORKFLOW));

    expect(() => setup("abcoder")).toThrow(
      'Unknown setup target "abcoder". Supported targets: gitnexus.',
    );
    expect(execSync).not.toHaveBeenCalled();
  });

  it("#4 lets GitNexus setup failures bubble", () => {
    fs.mkdirSync(path.join(tmpDir, DIR_NAMES.WORKFLOW));
    vi.mocked(execSync).mockImplementation(() => {
      throw new Error("gitnexus setup failed");
    });

    expect(() => setup("gitnexus")).toThrow("gitnexus setup failed");
  });
});
