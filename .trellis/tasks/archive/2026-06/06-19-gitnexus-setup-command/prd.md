# Replace GitNexus init flag with setup command

## Goal

Remove tl init --with-gitnexus and add tl setup gitnexus as the canonical external setup command.

## Requirements

- Remove `tl init --with-gitnexus` / `trellis init --with-gitnexus` from the public CLI surface and init implementation.
- Add `tl setup gitnexus` / `trellis setup gitnexus` as the canonical setup command for the GitNexus external capability.
- Require the command to run from an already initialized Trellis project, detected by the presence of `.trellis/`.
- Delegate GitNexus setup to `npx --yes gitnexus setup` with `cwd` set to the current project and `stdio: "inherit"` so GitNexus owns its own output and diagnostics.
- Reject unknown setup targets. The first supported target is only `gitnexus`.
- Do not write a Trellis-owned GitNexus enabled flag, do not run `gitnexus analyze`, do not add dry-run behavior, and do not preserve an init compatibility alias.
- Keep CLI users and desktop callers aligned by making the CLI command the behavior source.

## Acceptance Criteria

- [x] `trellis init --help` no longer advertises `--with-gitnexus`.
- [x] `setup("gitnexus")` invokes exactly `npx --yes gitnexus setup` once with `{ cwd, stdio: "inherit" }` when `.trellis/` exists.
- [x] `setup("gitnexus")` rejects before invoking GitNexus when the current directory is not initialized by Trellis.
- [x] Unknown setup targets reject before invoking any external command and mention supported targets.
- [x] GitNexus setup failures bubble to the CLI top-level catch without rewritten diagnostics.
- [x] Init integration tests no longer cover GitNexus setup as an init branch.
- [x] Setup integration tests cover success, missing Trellis project, unknown target, and child-process failure.
- [x] CLI/backend spec and GitNexus ADR describe `tl setup gitnexus` rather than `init --with-gitnexus`.

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.
