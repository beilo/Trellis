# Implementation Plan

## Scope

- `packages/cli/src/cli/index.ts`
- `packages/cli/src/commands/init.ts`
- `packages/cli/test/commands/init.integration.test.ts`
- Task planning/check artifacts under `.trellis/tasks/06-19-gitnexus-init-setup-flag/`

## Ordered Steps

1. Run GitNexus impact analysis before editing each modified symbol or file-adjacent symbol, per `AGENTS.md`.
2. Add `--with-gitnexus` to the `init` command registration.
3. Extend `InitOptions` with `withGitnexus?: boolean`.
4. Add a small required setup delegation path after normal init writes complete.
5. Add integration tests for:
   - default init does not invoke GitNexus setup
   - opt-in init invokes `npx --yes gitnexus setup`
   - setup failure rejects while `.trellis/` remains written
6. Run targeted test file.
7. Run broader validation if targeted tests pass.
8. Run GitNexus change detection before finishing code work.

## Validation Commands

```bash
pnpm --filter @mindfoldhq/trellis test -- test/commands/init.integration.test.ts
pnpm --filter @mindfoldhq/trellis typecheck
pnpm --filter @mindfoldhq/trellis lint
```

## Risk Points

- `node:child_process` is already used for Python and git probes; tests must distinguish those calls from the GitNexus setup call.
- Setup must run after writes so failure leaves Trellis files in place.
- The helper must not catch and downgrade setup failure to a warning.

## Rollback

Remove the CLI option, `InitOptions` field, setup delegation helper/call site, and the added integration tests.
