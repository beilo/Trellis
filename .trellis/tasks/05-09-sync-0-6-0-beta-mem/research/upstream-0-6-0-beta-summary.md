# Upstream 0.6.0 Beta Summary

## Version Evidence

- `npm view @mindfoldhq/trellis@beta version dist-tags --json` returned `0.6.0-beta.3` for the `beta` dist-tag.
- `git fetch --all --tags --prune` fetched upstream tags `v0.5.5` through `v0.6.0-beta.3`.
- `upstream/feat/v0.6.0-beta` points at `0b5a9dc`, tagged `v0.6.0-beta.3`.

## Relevant Upstream Commit Range

Range to sync from local baseline:

```bash
git log --oneline --no-merges v0.5.4..v0.6.0-beta.3
```

Key commits:

- `e1b368d feat(cli): add trellis mem for cross-platform AI conversation recall`
- `c10ded7 test(mem): add unit tests for trellis mem command`
- `4b90152 fix(mem): list/search --since respects cross-day session activity`
- `a16b8d9 feat(mem): tl mem extract --phase brainstorm|implement|all`
- `a992325 fix(mem): tl mem extract --phase dogfood-driven robustness + Codex support`
- `7e8f30c perf(mem): chunked sync streaming readJsonl + byte-prefix fast-reject`
- `f26c5fd fix(mem): OpenCode SQLite reader — restore visibility for 1.2+ users`

## Primary Files Expected From Upstream

- `packages/cli/src/commands/mem.ts`
- `packages/cli/test/commands/mem-*.test.ts`
- `packages/cli/src/cli/index.ts`
- `packages/cli/package.json`
- `pnpm-lock.yaml`
- `packages/cli/src/migrations/manifests/0.5.5.json` through `0.6.0-beta.3.json`
- `.trellis/spec/cli/backend/commands-mem.md`

## Local Fork Customizations To Preserve

- `install.sh`, `update.sh`, `LOCAL_INSTALL.md`
- Cursor codebase-search agent, rules, and `mcp.json` template wiring
- global-spec configurator and templates
- metrics scripts/specs/workspace behavior
- local AGENTS and workflow custom instructions
