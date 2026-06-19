import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import chalk from "chalk";
import { DIR_NAMES } from "../constants/paths.js";

const GITNEXUS_SETUP_COMMAND = "npx --yes gitnexus setup";
const SETUP_TARGETS = ["gitnexus"] as const;

type SetupTarget = (typeof SETUP_TARGETS)[number];

function isSetupTarget(target: string): target is SetupTarget {
  return SETUP_TARGETS.includes(target as SetupTarget);
}

function formatSetupTargets(): string {
  return SETUP_TARGETS.join(", ");
}

function assertTrellisProject(cwd: string): void {
  const workflowDir = path.join(cwd, DIR_NAMES.WORKFLOW);
  if (!fs.existsSync(workflowDir)) {
    throw new Error(
      `Cannot run setup outside a Trellis project. Run "trellis init" first.`,
    );
  }
}

function runGitnexusSetup(cwd: string): void {
  console.log(chalk.blue("🔗 Setting up GitNexus..."));
  execSync(GITNEXUS_SETUP_COMMAND, {
    cwd,
    stdio: "inherit",
  });
}

export function setup(target: string, cwd = process.cwd()): void {
  assertTrellisProject(cwd);

  if (!isSetupTarget(target)) {
    throw new Error(
      `Unknown setup target "${target}". Supported targets: ${formatSetupTargets()}.`,
    );
  }

  switch (target) {
    case "gitnexus":
      runGitnexusSetup(cwd);
      return;
  }
}
