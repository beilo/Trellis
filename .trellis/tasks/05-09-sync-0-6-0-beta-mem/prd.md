# sync 0.6.0 beta trellis mem

## Goal

Sync the local `custom/beilo-v0.5-rc` branch to upstream Trellis `v0.6.0-beta.3`, including the new `trellis mem` command and beta follow-up fixes, while preserving this fork's local customizations.

## What I already know

- npm `@mindfoldhq/trellis@beta` resolves to `0.6.0-beta.3`.
- Upstream tag `v0.6.0-beta.3` exists on `upstream/feat/v0.6.0-beta`.
- Local package version is `0.5.4` and current branch is `custom/beilo-v0.5-rc`.
- The key upstream command was introduced by `e1b368d feat(cli): add trellis mem for cross-platform AI conversation recall`.
- Follow-up beta commits add mem tests, `--since` cross-day filtering, `extract --phase`, Codex support, OpenCode SQLite 1.2 compatibility, and streaming JSONL performance work.
- The local fork has custom changes that must be kept: `install.sh`, `update.sh`, `LOCAL_INSTALL.md`, Cursor codebase-search/MCP/rules, global-spec templates, metrics scripts/specs, and local workflow/config customizations.

## Requirements

- Bring upstream release range `v0.5.5..v0.6.0-beta.3` into this branch.
- Include `trellis mem` CLI wiring, implementation, tests, lockfile/dependency updates, migration manifests, and relevant docs/spec updates.
- Preserve local fork-only customizations unless they directly conflict with upstream behavior.
- Keep Trellis-generated runtime data out of the release diff unless it is intentionally part of this sync task.
- Resolve conflicts by source of truth:
  - Upstream wins for `mem` implementation, beta manifests, release version, test coverage, and shared bug fixes.
  - Local fork wins for install/update script defaults, Cursor codebase-search/MCP, global-spec, metrics, and local custom branch docs.
  - For workflow/agent templates, merge behavior rather than blindly taking either side.

## Acceptance Criteria

- [ ] `packages/cli/package.json` reports `0.6.0-beta.3`.
- [ ] `packages/cli/src/commands/mem.ts` exists and `packages/cli/src/cli/index.ts` exposes `trellis mem`.
- [ ] Upstream beta manifests `0.5.5` through `0.6.0-beta.3` exist.
- [ ] Local custom files remain present after sync: `install.sh`, `update.sh`, `LOCAL_INSTALL.md`, Cursor codebase-search/MCP assets, global-spec templates, and metrics scripts/specs.
- [ ] `pnpm lint`, `pnpm typecheck`, and `pnpm test` pass, or failures are documented with a clear existing-vs-current boundary.
- [ ] A smoke command proves the built CLI exposes `trellis mem` help.

## Out of Scope

- Redesigning `trellis mem` beyond upstream behavior.
- Rewriting local install/update scripts beyond necessary version/branch compatibility.
- Publishing npm or creating an upstream PR.
- Removing fork-only local customizations that were intentionally added before this task.

## Technical Notes

- Upstream evidence is recorded in `research/upstream-0-6-0-beta-summary.md`.
- Current local dirty files before implementation: `.trellis/scripts/common/__pycache__/active_task.cpython-313.pyc` and `.trellis/workspace/codex/metrics-2026-05.jsonl`.
- `.trellis/tasks/**` is ignored by default in this repo; final commit will need `git add -f` for this task record.

## Implementation Summary

- Merged upstream `v0.6.0-beta.3` into `custom/beilo-v0.5-rc`.
- Added `trellis mem` CLI implementation, tests, manifests, and backend spec.
- Preserved local fork customizations for install/update scripts, Cursor codebase-search/MCP/rules, global-spec, and metrics.
- `trellis-check` corrected Codex workflow/config drift, `.trellis/.version`, `mem --phase` help/spec wording, and Cursor local-template regression coverage.

## Verification

- `pnpm lint`
- `pnpm typecheck`
- `pnpm test` — 35 files / 1111 tests passed after check fixes.
- `pnpm build`
- `node packages/cli/dist/cli/index.js mem --help`
- `git diff --cached --check && git diff --check`
