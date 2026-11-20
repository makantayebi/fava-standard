# Per-target layout forks

`fava-standard` has two tiers of versioning, not one:

- **`SCRIPT_VERSION`** (root of the repo) + **`versions/`** — the shared
  base script. One `layout.yaml` per version, used as-is by any target
  that has no reason to diverge. Changes here are meant to apply
  everywhere (new disambiguation marks, vowel handling, anything about
  the *language*, not the platform).
- **`layouts/<target>/`** (this directory) — a target that has actually
  diverged from the base script for reasons specific to that platform.
  Each target under here gets its **own independent version number**,
  starting from whatever base version it forked at. A change here is
  scoped to that one target only — it does not bump `SCRIPT_VERSION`
  and does not affect any other target, forked or not.

Android, iOS, Windows, macOS, Ubuntu, US-ANSI vs EU-ISO — these are
real physical/platform differences, and their layouts are expected to
diverge over time (a touchscreen keyboard has different ergonomics
than a physical one; a physical ISO board has keys a US-ANSI board
doesn't). This directory is where that divergence lives once a target
actually needs it — not before. A target with no fork yet (e.g.
`ubuntu-us-ansi` today) has no folder here at all; it just tracks the
base `versions/` directly, per `targets.yaml`.

## Rendering

```bash
python3 tools/render.py v0.0.6 --target android
```

writes `layouts/android/v0.0.6/generated/` — only the artifacts that
target actually uses (for android: `avayi_keys.xml`,
`avayi_keys_shifted.xml`, `android_layout.svg`). Add a target to
`TARGET_ARTIFACTS` in `tools/render.py` when a new one starts forking.

## Forking a new target

1. `mkdir -p layouts/<name>/<version>/`
2. Copy the base `layout.yaml` you're forking from into it, and add a
   `target:` / `forked_from_script_version:` header (see
   `layouts/android/v0.0.6/layout.yaml` for the convention).
3. Make the platform-specific change.
4. Add `<name>` to `TARGET_ARTIFACTS` in `tools/render.py` with
   whatever render function(s) that platform needs, if it's the first
   fork for that target.
5. Update `targets.yaml`: add `layout_version` (this fork's own version)
   and `forked_from_script_version` (which base version it diverged
   from) to that target's entry.
