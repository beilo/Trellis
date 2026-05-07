import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { getAllAgents } from "../../src/templates/cursor/index.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../../../..");

const EXPECTED_AGENT_NAMES = [
  "codebase-search",
  "trellis-check",
  "trellis-implement",
  "trellis-research",
];

describe("cursor getAllAgents", () => {
  it("returns the expected agent set including local codebase search", () => {
    // 中文注释：本地分支额外维护 codebase-search，不能被上游 Cursor agent 集合覆盖掉。
    const agents = getAllAgents();
    const names = agents.map((a) => a.name).sort();
    expect(names).toEqual(EXPECTED_AGENT_NAMES);
  });
});

describe("cursor agents frontmatter single-line description", () => {
  for (const name of EXPECTED_AGENT_NAMES) {
    it(`${name}.md frontmatter description is a single-line literal`, () => {
      // 中文注释：Cursor agent UI 只稳定识别单行 description，禁止 YAML 块标量。
      const filePath = path.join(
        repoRoot,
        "packages/cli/src/templates/cursor/agents",
        `${name}.md`,
      );
      const content = fs.readFileSync(filePath, "utf-8");
      const fm = content.split("---\n")[1] ?? "";

      expect(fm).not.toMatch(/^description:\s*\|\s*$/m);
      expect(fm).not.toMatch(/^description:\s*>\s*$/m);

      const descMatch = fm.match(/^description:\s*(.+)$/m);
      expect(
        descMatch,
        `${name}.md must have 'description: <text>' on a single line`,
      ).not.toBeNull();
      const descValue = descMatch ? descMatch[1] : "";
      expect(descValue.trim()).not.toBe("|");
      expect(descValue.trim()).not.toBe(">");
      expect(descValue.length).toBeGreaterThan(0);
    });
  }
});
