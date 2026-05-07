# Research: sync 0.5.0 through 0.5.4 into custom branch

- Query: How to sync upstream v0.5.0 GA through v0.5.4 into `custom/beilo-v0.5-rc` while preserving local customizations?
- Scope: internal
- Date: 2026-05-07

## Findings

### Current branch and range

- Current branch: `custom/beilo-v0.5-rc`
- Current HEAD: `47e6f0fbbb81067161a8fbadaba21b8c20024f33`
- `v0.5.4`, `upstream/main`, and `upstream/feat/v0.5` all resolve to `8afc24ecc66581b7fb5f350f602e517fb0c08956`.
- Merge base of `HEAD` and `v0.5.4`: `8b4199bcd1dd7fc45b55c478a368d589b3211435`, described as `v0.5.0-rc.2`.
- Current package version is `0.5.0-rc.2`; upstream `v0.5.4` package version is `0.5.4`.

Important implication: although the product requirement says "0.5.0 GA to 0.5.4", this branch forked at `v0.5.0-rc.2`, so implementation must include the missing pre-GA rc.3-rc.7 prerequisites as well as GA-to-0.5.4 fixes.

### Upstream commit ranges

Pre-GA prerequisites missing from this branch (`v0.5.0-rc.2..v0.5.0`):

- `9a4c53b` fix Gemini CLI 0.40.x template schema.
- `8a39265` fix class-2 sub-agents discovering active task on session mismatch.
- `a7d6546` strip `*_PROJECT_DIR` env vars in tests.
- `cb8a076` add `TRELLIS_HOOKS=0` / `TRELLIS_DISABLE_HOOKS=1`.
- `f98d9bf`, `2b9e96d`, `180ec08`, `3964df4` normalize MSYS/Git-Bash/Cygwin/WSL paths in session-start hooks.
- `fbb64c2` enable Codex `multi_agent_v2` default and 8-minute wait floor.
- `0b1245a` make finish-work tolerate unrelated dirty paths from parallel windows.
- `a539859` Codex Linux EPERM tolerance and OpenCode plugin version bump.
- `52e4ace` docs-site release lifecycle scripts/create-manifest gotchas.
- Release manifests/tags: `0.5.0-rc.3` through `0.5.0`, ending at `75b3d62`.

GA-to-0.5.4 range (`v0.5.0..v0.5.4`):

- `4165b3a` and `6a1bb18`: block Codex/shared-hook sub-agent recursion.
- `3a56e9a`: Cursor agent frontmatter description single-line fix.
- `3f1711b`: Python <=3.11 f-string backslash crash fix in session-start.
- `6272a9e`, `1adb7b0`, `5b298ba`: class-1 sub-agent marker fallback and degraded-mode `task.py start`.
- `c64d158`: `compareVersions` preserves hyphens inside prerelease identifiers and adds tests.
- `2c70346`: workflow and agent recursion guards across platforms plus `0.5.4` manifest.
- `59810ee`: clearer user-facing `0.5.4` manifest changelog.
- `8afc24e`: package version bump to `0.5.4`.

### Files found

- `packages/cli/src/utils/compare-versions.ts` - semver comparison utility still uses `split("-", 2)` and drops hyphenated prerelease suffixes.
- `packages/cli/test/utils/compare-versions.test.ts` - absent locally; upstream adds this unit test file.
- `packages/cli/src/migrations/manifests/0.5.0-rc.3.json` through `0.5.4.json` - absent locally; upstream adds all release manifests in this range.
- `packages/cli/src/templates/cursor/agents/codebase-search.md` - local customization; upstream does not have it and a naive direct diff shows it as deleted.
- `packages/cli/src/templates/cursor/mcp.json` - local customization; upstream does not have it.
- `packages/cli/src/templates/cursor/rules/codebase-search.mdc` - local customization; upstream does not have it.
- `packages/cli/src/configurators/cursor.ts` - local customization writes Cursor rules and MCP config.
- `packages/cli/src/templates/cursor/index.ts` - local customization exposes Cursor `mcp.json` and `rules/` helpers.
- `packages/cli/src/configurators/global-spec.ts` and `packages/cli/src/templates/global-spec/**` - local customization for machine-level `~/.trellis/spec/` deployment.
- `install.sh`, `update.sh`, `LOCAL_INSTALL.md` - local install/update customization; upstream direct diff shows them as deleted.
- `.codex/agents/*`, `.claude/agents/*`, `.cursor/agents/*`, `.trellis/workflow.md`, `packages/cli/src/templates/*/agents/*` - recursion guard surface.

### Code patterns

- Current `compareVersions` splits prerelease with `a.split("-", 2)` and `b.split("-", 2)`, which truncates `1.0.0-alpha-1` to prerelease `alpha`; see `packages/cli/src/utils/compare-versions.ts:11`.
- Cursor local customization imports `getMcpConfig` and `getRules` from the template module; see `packages/cli/src/configurators/cursor.ts:13`.
- Cursor init writes `.cursor/rules/*.mdc` from template files; see `packages/cli/src/configurators/cursor.ts:49`.
- Cursor init writes `.cursor/mcp.json`; see `packages/cli/src/configurators/cursor.ts:64`.
- Cursor template index currently lists files under `rules/` and exports `getMcpConfig`; see `packages/cli/src/templates/cursor/index.ts:13`.
- Local global-spec deploy writes all template files to `~/.trellis/spec/` on init; see `packages/cli/src/configurators/global-spec.ts:21`.
- Local global-spec update creates missing files and skips modified existing files; see `packages/cli/src/configurators/global-spec.ts:43`.
- `init.ts` dynamically imports and runs `deployGlobalSpec()` after platform configuration; see `packages/cli/src/commands/init.ts:1635`.
- `update.ts` dynamically imports and runs `syncGlobalSpec()` after template update reporting; see `packages/cli/src/commands/update.ts:2288`.
- Cursor update tracking includes `.cursor/mcp.json` and `.cursor/rules/*.mdc`; see `packages/cli/src/configurators/index.ts:198`.
- Tests already expect `.cursor/rules/*` to be a managed path; see `packages/cli/test/configurators/index.test.ts:63`.

### Conflict / risk analysis

`git diff HEAD..v0.5.4` is noisy and misleading for this task: it reports many local custom files as deleted because upstream does not know about them. Do not use that diff as an apply plan.

`git merge-tree $(git merge-base HEAD v0.5.4) HEAD v0.5.4` gives a better conflict forecast. It reports true changed-in-both hotspots:

- `packages/cli/src/commands/init.ts`: upstream adds Python EPERM/sandbox escape-hatch behavior while local branch adds global-spec deployment.
- `packages/cli/src/commands/update.ts`: upstream narrows Codex upgrade detection and adds other update behavior while local branch adds global-spec sync.
- `packages/cli/src/configurators/index.ts`: upstream moves Gemini shared skills to `.agents/skills` and adds neutral placeholder helpers; local branch adds Cursor MCP/rules template collection.
- `packages/cli/src/templates/cursor/agents/trellis-check.md`: upstream adds recursion guard and hook marker context-loading protocol; local branch has Cursor template edits.
- `packages/cli/src/templates/cursor/agents/trellis-implement.md`: same risk as check.
- `packages/cli/src/templates/cursor/agents/trellis-research.md`: direct content conflict around local `model: gpt-5.3-codex-spark`; keep the local model field while accepting upstream formatting/frontmatter fixes unless PRD says otherwise.

High-risk local customizations to explicitly preserve:

- Cursor codebase-search: `.cursor/agents/codebase-search.md`, `packages/cli/src/templates/cursor/agents/codebase-search.md`, and `packages/cli/src/templates/cursor/rules/codebase-search.mdc`.
- Cursor MCP template: `.cursor/mcp.json`, `packages/cli/src/templates/cursor/mcp.json`, `getMcpConfig()`, and the `.cursor/mcp.json` update-hash entry.
- Global spec: `packages/cli/src/configurators/global-spec.ts`, `packages/cli/src/templates/global-spec/**`, init deployment, update sync, and related tests if present.
- Local install/update: `install.sh`, `update.sh`, and `LOCAL_INSTALL.md`.
- Metrics local customization: `.trellis/spec/guides/metrics.md`, `.trellis/scripts/metrics.py`, `.trellis/scripts/hooks/metrics_log.py`; upstream direct diff deletes them, so decide separately whether they are still required before any removal.

### Recommended implementation strategy

Do not direct-merge or direct-reset to `v0.5.4`. The merge base is old, the upstream range touches many generated templates, and the direct diff would drop local customizations.

Use manual patching by feature cluster, with upstream as reference:

1. Sync core release prerequisites from rc.3-rc.7 that are still behaviorally relevant:
   - Gemini 0.40 template/schema and `.agents/skills` neutral rendering.
   - class-2 active-task fallback / marker fallback.
   - `TRELLIS_HOOKS=0`.
   - Windows path normalization in session-start hooks.
   - Codex `multi_agent_v2` config and Python EPERM tolerance.
   - finish-work dirty-path classification.
2. Sync release manifests `0.5.0-rc.3.json` through `0.5.4.json` by copying upstream files, then keep local manifest continuity checks green.
3. Apply `compareVersions` fix from `c64d158` and add upstream `packages/cli/test/utils/compare-versions.test.ts`.
4. Apply recursion guard from `2c70346` to:
   - root generated files: `.trellis/workflow.md`, `.codex/agents/*`, `.cursor/agents/*`, `.claude/agents/*` if this repo dogfoods them.
   - template files under `packages/cli/src/templates/{claude,codebuddy,codex,cursor,droid,gemini,kiro,opencode,pi,qoder}/`.
   - shared hooks / session-start templates that inject main-session dispatch guidance.
5. While editing Cursor files, merge upstream agent/template changes into the local codebase-search/MCP/rules branch shape rather than accepting upstream deletion.
6. Keep package version bump to `0.5.4` only after the functional sync and manifests are in place.

Cherry-pick guidance:

- Cherry-pick is acceptable only for isolated, low-conflict commits like `c64d158` if the implementer is ready to resolve tests.
- Avoid cherry-picking broad commits like `2c70346` wholesale because it includes task archive/journal/docs-site submodule noise and generated template files; manually port the relevant hunks.
- Avoid merging `v0.5.4` wholesale unless the implementer first snapshots and restores local-only files. A merge will require conflicts and may still silently remove local customizations that upstream never had.

### Verification commands

Core verification:

```bash
pnpm lint
pnpm typecheck
pnpm test
```

Targeted regression tests:

```bash
pnpm test packages/cli/test/utils/compare-versions.test.ts
pnpm test packages/cli/test/regression.test.ts
pnpm test packages/cli/test/templates/trellis.test.ts
pnpm test packages/cli/test/templates/codex.test.ts
pnpm test packages/cli/test/templates/cursor.test.ts
pnpm test packages/cli/test/templates/shared-hooks.test.ts
pnpm test packages/cli/test/configurators/index.test.ts
pnpm test packages/cli/test/configurators/platforms.test.ts
pnpm test packages/cli/test/configurators/shared.test.ts
```

Manual/structural checks after implementation:

```bash
node -p "require('./packages/cli/package.json').version"
ls packages/cli/src/migrations/manifests/0.5.0-rc.{3,4,5,6,7}.json
ls packages/cli/src/migrations/manifests/0.5.{0,1,2,3,4}.json
rg -n "Recursion Guard|Sub-agent self-exemption|Do NOT spawn another" packages/cli/src/templates .codex .cursor .claude .trellis/workflow.md
rg -n "splitOnFirstHyphen|alpha-1|alpha-2" packages/cli/src/utils/compare-versions.ts packages/cli/test
rg -n "getMcpConfig|getRules|global-spec|deployGlobalSpec|syncGlobalSpec|codebase-search" packages/cli/src packages/cli/test
```

Preservation checks:

```bash
test -f packages/cli/src/templates/cursor/agents/codebase-search.md
test -f packages/cli/src/templates/cursor/mcp.json
test -f packages/cli/src/templates/cursor/rules/codebase-search.mdc
test -f packages/cli/src/configurators/global-spec.ts
test -f install.sh
test -f update.sh
test -f LOCAL_INSTALL.md
```

## External References

- No web references were used. Evidence came from local git refs/tags and repository files.
- Local version refs: `v0.5.0-rc.2`, `v0.5.0`, `v0.5.4`, `upstream/main`, `upstream/feat/v0.5`.

## Related Specs

- `.trellis/workflow.md` - Trellis task workflow and sub-agent routing.
- `.trellis/spec/cli/backend/index.md` - backend guideline index.
- `.trellis/spec/cli/backend/migrations.md` - migration manifest contract.
- `.trellis/spec/cli/backend/platform-integration.md` - platform template/configurator architecture.
- `.trellis/spec/cli/backend/quality-guidelines.md` - TypeScript and lint standards.
- `.trellis/spec/cli/unit-test/index.md` - test guideline index.
- `.trellis/spec/cli/unit-test/conventions.md` - when to write tests and test conventions.

## Caveats / Not Found

- No source files were changed by this research; only this research file was written.
- `git merge-tree` is a conflict forecast, not proof that a real merge is safe. It is useful here mainly to separate true changed-in-both conflicts from local-only files that a direct diff shows as deleted.
- The current session has no active Trellis task pointer (`task.py current --source` returned none). The research path was provided explicitly by the parent task dispatch, so output was written there.
- Memory lookup found no directly relevant prior notes for this exact `sync-0-5-4-features` task.
