# fava-standard

The source of truth for the **Fava** Persian keyboard layout.

If you're deciding what a key should do, or implementing Fava on a new
platform, this is the repo that settles it — not `windows-keyboard`, not
`ubuntu-keyboard`, not whatever's currently installed on someone's
machine. Those are downstream of this one.

## How this works

Two independent things get versioned here, not one:

```
SCRIPT_VERSION      <- the abstract Fava design, platform-agnostic
versions/
  v0.0.1/
    layout.yaml     <- the definition: every physical key, what it types
    notes.md        <- why, in prose
    generated/      <- output of tools/render.py, checked in for convenience
  v0.0.5/
    layout.yaml
    notes.md
    generated/

layouts/            <- per-TARGET layouts, each with its OWN version number
  android/
    v0.0.7/
      layout.yaml   <- forked from a base version, diverging for
                       reasons specific to that platform
      generated/
  ubuntu-us-ansi/
    v0.0.5/
      layout.yaml   <- identical to base 0.0.5 today (no divergence
                       yet), but still its own tracked copy, not a
                       special case
      generated/

targets.yaml        <- which script/layout version each target is on
schema/
  layout.schema.md  <- the layout.yaml format, field by field
tools/
  render.py         <- layout.yaml -> .xkb_symbols / Android XML / SVG diagrams
reference/
  (original design docs, pre-dating this repo's structure)
```

- **Script version** (`SCRIPT_VERSION`, `versions/`) — the shared,
  platform-agnostic design: which marks exist, what each one means, the
  Q/W/E rotation, the وْ convention. Changes here are meant to apply
  *everywhere*.
- **Layout version** (`layouts/<target>/`) — one target's own fork,
  independently versioned, for a change that's specific to that
  platform and doesn't belong in the shared script (Android's extra
  backspace key, its ۱۲۳ symbols page — a physical keyboard doesn't
  need either). A target with no reason to diverge still gets its own
  folder here (see `ubuntu-us-ansi`), it just stays identical to
  whatever base version it tracks. See `layouts/README.md` for the full
  model, including how to fork a new target.

- **A version is immutable once it has a folder.** Deciding to change a
  key means creating a new version folder, not editing an old one.
- **`layout.yaml` is the only hand-edited input.** Everything in a
  version's `generated/` comes from running `tools/render.py` against
  it — never hand-edit those files, re-run the tool instead.
- **Every platform repo implements the latest version.** If
  `ubuntu-keyboard`'s `.xkb_symbols` and this repo's latest
  `layout.yaml` disagree, this repo is right and that file is stale and
  needs updating (ideally by running `tools/render.py` and copying its
  output over, not by hand-patching).

## Versioning

`major.minor.patch`, as a folder name and a matching Git tag — but
we're deliberately still at **major version 0**, meaning every change
just bumps the trailing digit (`0.0.1` → `0.0.2` → `0.0.3`...)
regardless of how big it is. This isn't an oversight: per
[SemVer itself](https://semver.org/#spec-item-4), "major version zero
(0.y.z) is for initial development... anything MAY change at any time."
The layout is still actively being redesigned key by key — claiming a
`1.0.0` right now would assert a stability this doesn't have yet.

Once the design is actually settled enough to commit to, `1.0.0` gets
declared deliberately, and *from that point on*:
- **major** — a key does something semantically different (a different
  letter, mark, or symbol than before).
- **minor** — new keys/behavior added without changing existing ones.
- **patch** — a correction to documentation/metadata, no behavior change.

There are five versions so far. `v0.0.1` is the original Windows design;
`v0.0.2` is a substantial reassignment of several keys developed while
building the Ubuntu port — see `versions/v0.0.2/notes.md`, which also
documents an unintentional Y/Z mixup discovered along the way. `v0.0.3`
adds shift+Q/W/E as one-keystroke disambiguated vowels, implemented via
Compose rather than a plain key binding — see `versions/v0.0.3/notes.md`
for the mechanism. `v0.0.4` splits و's consonant/vowel ambiguity by
repurposing سکون, assigned to the key freed in `v0.0.3` — see
`versions/v0.0.4/notes.md` for why several other options were rejected
first. `v0.0.5` collapses that into one keystroke: B now types وْ
directly. Read `v0.0.2`'s notes first if you want the full, slightly
messy, honest history behind where things currently stand.

## Script version vs. layout version (vs. app version)

Three independent things can appear per target, tracked in `targets.yaml`:

- **Script version** (`SCRIPT_VERSION`, `versions/`) — the shared,
  platform-agnostic design: which marks exist, what each one means, the
  Q/W/E rotation, the وْ convention. A target with `script_version` set
  tracks this directly — no fork, no divergence.
- **Layout version** (`layouts/<target>/`, plus `layout_version` +
  `forked_from_script_version` in `targets.yaml`) — set *instead of*
  `script_version` once a target has forked its own layout for
  platform-specific reasons. `layout_version` is that fork's own
  version number; `forked_from_script_version` records which base
  version it diverged from.
- **App version** (`app_version`) — a target's own release version for
  the actual shipped app/installer (only targets with a real app have
  this — e.g. Android's `app/build.gradle.kts`). Moves on UI/bug-fix
  changes that don't touch any `layout.yaml` at all, forked or not.

As of this writing: `android` has forked (`layout_version: 0.0.7`,
`forked_from_script_version: 0.0.5`) — its extra backspace key and ۱۲۳
symbols page don't belong in the shared script, since a physical
keyboard doesn't need either. `ubuntu-us-ansi` has its own tracked copy
under `layouts/` too, but is still identical to base `0.0.5` — no
actual divergence yet. See `targets.yaml` for current status per
target, `layouts/README.md` for the fork model and how to add a new
one, and `TODO.md` for targets that don't exist yet.

## Using `tools/render.py`

```bash
pip install pyyaml   # the only dependency
python3 tools/render.py v0.0.2
#   -> versions/v0.0.2/generated/avayi.xkb_symbols
#   -> versions/v0.0.2/generated/layout.svg

python3 tools/render.py v0.0.2 --compare v0.0.1
#   -> also: versions/v0.0.2/generated/vs-v0.0.1.svg (both, stacked)
```

Currently generates: an XKB `.xkb_symbols` block (Linux), and SVG
keyboard diagrams. Does **not** yet generate a Windows `.klc` — that's
unbuilt future work (see `versions/v0.0.2/notes.md`, "Known gaps").

## Reference material

- [`linguistic-basis.md`](reference/linguistic-basis.md) — what kind of
  project this is in actual linguistic terms (an *orthographic reform*
  targeting Persian's *impure abjad* vowel gap), and the closest
  real-world precedent (Sorani Kurdish). Start here if you want the
  academic grounding for the movement.
- [`persian-phonology.md`](reference/persian-phonology.md) /
  [`persian-phonemes.yaml`](reference/persian-phonemes.yaml) — every
  letter and diacritic's actual Persian pronunciation (not Arabic),
  sourced and cross-checked. Input to future `layout.yaml` decisions,
  not itself a Fava spelling definition.
- The two `.docx` files predate this repo's structure entirely; kept for
  historical context, not treated as authoritative.
