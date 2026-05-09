# Merge Conflict Plan

## Probe Command

The merge probe ran in `/tmp/Trellis-060-probe`:

```bash
git merge --no-commit --no-ff v0.6.0-beta.3
```

## Conflict Files

Conflict files observed:

- `.claude/agents/trellis-check.md`
- `.claude/agents/trellis-implement.md`
- `.claude/hooks/session-start.py`
- `.codex/agents/trellis-check.toml`
- `.codex/agents/trellis-implement.toml`
- `.codex/config.toml`
- `.codex/hooks/session-start.py`
- `.cursor/agents/trellis-check.md`
- `.cursor/agents/trellis-implement.md`
- `.cursor/hooks/session-start.py`
- `.trellis/scripts/task.py`
- `packages/cli/package.json`
- `packages/cli/src/commands/init.ts`
- `packages/cli/src/configurators/shared.ts`
- `packages/cli/src/templates/codex/agents/trellis-check.toml`
- `packages/cli/src/templates/codex/agents/trellis-implement.toml`
- `packages/cli/src/templates/codex/config.toml`
- `packages/cli/src/templates/cursor/agents/trellis-research.md`
- `packages/cli/src/templates/droid/droids/trellis-check.md`
- `packages/cli/src/templates/droid/droids/trellis-implement.md`
- `packages/cli/src/templates/kiro/agents/trellis-check.json`
- `packages/cli/src/templates/kiro/agents/trellis-implement.json`
- `packages/cli/src/templates/trellis/scripts/task.py`
- `packages/cli/src/templates/trellis/workflow.md`
- `packages/cli/test/configurators/index.test.ts`
- `packages/cli/test/configurators/platforms.test.ts`
- `packages/cli/test/configurators/shared.test.ts`
- `packages/cli/test/regression.test.ts`
- `packages/cli/test/templates/cursor.test.ts`

## Resolution Policy

- Keep upstream for `trellis mem` implementation, beta manifests, `package.json` version, and upstream test additions.
- Keep local fork customizations for `install.sh`, `update.sh`, `LOCAL_INSTALL.md`, Cursor codebase-search/MCP/rules, global-spec templates, metrics scripts/specs, and local documentation of those customizations.
- For agent and workflow templates, merge semantics:
  - Keep upstream 0.6 fixes for Codex hook/config changes, recursion guards, inline/default dispatch changes, OpenCode compatibility, and beta workflow changes.
  - Preserve local branch-specific instructions only where they are not contradicted by upstream 0.6 fixes.
- For `.trellis/tasks` and `.trellis/workspace`, avoid importing unrelated upstream dogfood task history unless it is required for this sync task.
- Remove generated `__pycache__` changes before final commit unless they were already intentionally tracked and must be preserved.

## Fast Verification Targets

- `rg -n "command\\(\"mem\"|mem\\.command|runMem" packages/cli/src/cli/index.ts packages/cli/src/commands/mem.ts`
- `node -e "console.log(require('./packages/cli/package.json').version)"`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm build && node packages/cli/dist/cli/index.js mem --help`
