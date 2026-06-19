# Implementation Plan

1. Start the Trellis task after this plan is written.
2. Run GitNexus impact checks for the existing symbols that will be edited:
   - `init`
   - `InitOptions`
   - `program`
3. Remove GitNexus setup handling from `init.ts` and CLI init options.
4. Add `commands/setup.ts` and register `setup <target>` in `cli/index.ts`.
5. Remove old init GitNexus tests and add setup integration tests.
6. Update `.trellis/spec/cli/backend/platform-integration.md` from the init flag contract to setup command contract.
7. Run focused tests and quality commands:
   - CLI setup/init command tests
   - `pnpm --filter @mindfoldhq/trellis typecheck`
   - `pnpm --filter @mindfoldhq/trellis lint`
   - `pnpm --filter @mindfoldhq/trellis build`
8. Run `npx --no-install gitnexus detect-changes --scope all` before committing.
9. Commit with branch suffix and push `beilo/main`.
