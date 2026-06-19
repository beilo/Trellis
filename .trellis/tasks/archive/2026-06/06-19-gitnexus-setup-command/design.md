# Design

## Command Surface

Add a top-level command:

```bash
trellis setup <target>
tl setup <target>
```

The first supported target is `gitnexus`. `init` remains only Trellis project onboarding.

## Implementation

- Add `packages/cli/src/commands/setup.ts`.
- Export `setup(target: string, cwd = process.cwd()): void`.
- Keep a small target whitelist in the setup command module. Unknown targets fail before any subprocess runs.
- Check for `.trellis/` before target setup. A setup target configures an existing Trellis project; it does not create one.
- For GitNexus, run:

```typescript
execSync("npx --yes gitnexus setup", { cwd, stdio: "inherit" });
```

No catch is added around the child process. The CLI action catch prints the error message and exits 1, while GitNexus output remains inherited.

## Removed Behavior

- Remove `--with-gitnexus` from `init`.
- Remove `withGitnexus` from `InitOptions`.
- Remove init-owned GitNexus setup helper and tests.
- Do not add a compatibility alias.

## Documentation

Update the CLI/backend platform integration spec to describe setup commands for external capabilities. Keep the ADR and glossary aligned with the agreed terms:

- Setup Command
- Setup Target
- Delegated MCP Setup
- Stateless Integration Enablement

## Validation

Run focused command tests, typecheck, lint, build, and GitNexus change detection.
