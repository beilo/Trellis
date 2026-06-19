# Add GitNexus init setup flag

## Goal

Add `tl init --with-gitnexus` as an explicit opt-in entry point for GitNexus setup during new Trellis project initialization.

The flag should let users initialize Trellis normally, then delegate GitNexus MCP setup to GitNexus by running `npx --yes gitnexus setup`.

## User Value

Users who want Trellis plus GitNexus code intelligence can enable the integration at project creation time with one explicit flag, while Trellis keeps ownership boundaries clear and avoids becoming a GitNexus wrapper.

## Confirmed Facts

- The accepted first shape is documented in `CONTEXT.md` and `docs/adr/0001-gitnexus-setup-delegation.md`.
- Existing CLI init implementation lives in `packages/cli/src/commands/init.ts`.
- CLI argument registration lives in `packages/cli/src/cli/index.ts`.
- Init integration tests live in `packages/cli/test/commands/init.integration.test.ts` and already mock `node:child_process`.
- GitNexus setup is delegated with `npx --yes gitnexus setup`.

## Requirements

- Add a `--with-gitnexus` flag to `trellis init` / `tl init`.
- Represent the flag in init options as `withGitnexus?: boolean`.
- After normal Trellis init writes complete, run `npx --yes gitnexus setup` when the flag is present.
- Run GitNexus setup from the same working directory as init.
- If GitNexus setup exits nonzero, the init command fails.
- Do not roll back Trellis files already written before GitNexus setup fails.
- Do not call `gitnexus analyze`.
- Do not add `tl update --with-gitnexus`.
- Do not write GitNexus instructions into `AGENTS.md`.
- Do not manage `.gitnexus/`, root `.gitignore`, GitNexus indexes, or a Trellis config flag.
- Tests must verify setup invocation and failure behavior without running real `npx`.

## Acceptance Criteria

- [x] `trellis init --help` exposes `--with-gitnexus` with clear wording.
- [x] Calling `init({ yes: true, withGitnexus: true })` invokes `execSync("npx --yes gitnexus setup", { cwd, stdio: "inherit" })` after normal init files are written.
- [x] When the GitNexus setup command throws, `init()` rejects and previously written Trellis files remain on disk.
- [x] `init({ yes: true })` does not invoke GitNexus setup.
- [x] The implementation does not add update support, GitNexus indexing, GitNexus instruction generation, `.gitnexus/` management, `.gitignore` management, or Trellis config state.
- [x] Targeted init integration tests pass.

## Notes

- Existing untracked documentation artifacts from the prior discussion are intentionally preserved: `CONTEXT.md` and `docs/adr/0001-gitnexus-setup-delegation.md`.
