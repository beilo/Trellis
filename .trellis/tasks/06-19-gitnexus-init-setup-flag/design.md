# Design: GitNexus Init Setup Flag

## Boundary

Trellis owns only the explicit opt-in flag and the timing of delegation. GitNexus owns MCP configuration details, indexing, generated instructions, `.gitnexus/` contents, and any ignore rules it needs.

## CLI Contract

Add `--with-gitnexus` to the existing `init` command in `packages/cli/src/cli/index.ts`. Commander will pass it as `options.withGitnexus`, matching the existing camel-cased option convention.

Add `withGitnexus?: boolean` to `InitOptions` in `packages/cli/src/commands/init.ts`.

## Execution Flow

The normal init flow remains unchanged until after `createWorkflowStructure()` and the existing post-write init steps have run.

When `options.withGitnexus` is true, run:

```bash
npx --yes gitnexus setup
```

Use `execSync` with:

- `cwd`: the init working directory
- `stdio`: `inherit`

This makes the delegated setup behave like a required child command. A nonzero exit throws through the existing top-level CLI catch, causing the init command to fail with exit code 1.

## Failure Semantics

GitNexus setup is post-write setup. If it fails, Trellis does not attempt rollback. This matches the ADR: Trellis project files may already exist, and the user can retry GitNexus setup directly or rerun init behavior as appropriate.

## Non-goals

- No `trellis update --with-gitnexus`.
- No `gitnexus analyze`.
- No Trellis-authored GitNexus instruction block.
- No Trellis-owned `.gitnexus/` or `.gitignore` mutation.
- No `.trellis/config.yaml` integration enabled flag.

## Compatibility

The default `trellis init` path remains unchanged. The new behavior is only activated by `--with-gitnexus`.

## Test Strategy

Use the existing `init.integration.test.ts` pattern: direct function calls in temp directories with `node:child_process` mocked. Assert the delegated command is present only with `withGitnexus: true`; assert failure rejects while Trellis files remain on disk.
