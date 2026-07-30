# Beilo Release Map

This repository keeps a Beilo-owned release line on top of upstream Trellis.
Beilo versions are independent from upstream Trellis versions.

## Versioning Policy

- Beilo versions start at `0.0.1` and increment on every Beilo release.
- Upstream Trellis versions are recorded as baselines, not reused as Beilo versions.
- A Beilo release may contain only an upstream sync, only Beilo-local changes, or both.
- Keep upstream package versions unchanged unless we explicitly decide to publish Beilo packages.
- Use tags in the form `beilo-v<version>`, for example `beilo-v0.0.1`.

## Release Map

| Beilo version | Beilo tag | Upstream baseline | Upstream commit/tag | Sync commit | Date | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0.1 | `beilo-v0.0.1` | Trellis `0.6.0` | `v0.6.0` / `f2cc0745` | `a330cd37` | 2026-06-17 | Initial Beilo release line. Syncs upstream Trellis 0.6.0 GA into the Beilo branch. |
| 0.0.2 | `beilo-v0.0.2` | Trellis `0.6.10` | `v0.6.10` / `c94d6fc2` | `4bf99046` | 2026-07-30 | Syncs upstream 0.6.10 and lets Codex channel workers inherit native multi-agent settings without child-thread terminal-event leakage. |

## Update Checklist

1. Fetch upstream tags and branches.
2. Merge or cherry-pick the desired upstream baseline into `beilo/main`.
3. Apply Beilo-local changes if needed.
4. Add a new row to this file with the Beilo version and upstream baseline.
5. Tag the release as `beilo-v<version>`.
6. Push `beilo/main` and the tag to `origin`.
