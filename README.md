# fava-doc

The source of truth for the **Fava** Persian keyboard layout.

If you're deciding what a key should do, or implementing Fava on a new
platform, this is the repo that settles it — not `windows-keyboard`, not
`ubuntu-keyboard`, not whatever's currently installed on someone's
machine. Those are downstream of this one.

## How this works

```
versions/
  v1.0.0/
    layout.yaml     <- the definition: every physical key, what it types
    notes.md        <- why, in prose
    generated/      <- output of tools/render.py, checked in for convenience
  v2.0.0/
    layout.yaml
    notes.md
    generated/
schema/
  layout.schema.md  <- the layout.yaml format, field by field
tools/
  render.py         <- layout.yaml -> .xkb_symbols + SVG diagrams
reference/
  (original design docs, pre-dating this repo's structure)
```

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

Plain `major.minor.patch`, as a folder name and a matching Git tag:
- **major** — a key does something semantically different (a different
  letter, mark, or symbol than before).
- **minor** — new keys/behavior added without changing existing ones.
- **patch** — a correction to documentation/metadata, no behavior change.

There are two versions so far. `v1.0.0` is the original Windows design;
`v2.0.0` is a substantial reassignment of several keys developed while
building the Ubuntu port — see `versions/v2.0.0/notes.md`, which also
documents an unintentional Y/Z mixup discovered along the way. Read that
one first if you want the full, slightly messy, honest history.

## Using `tools/render.py`

```bash
pip install pyyaml   # the only dependency
python3 tools/render.py v2.0.0
#   -> versions/v2.0.0/generated/avayi.xkb_symbols
#   -> versions/v2.0.0/generated/layout.svg

python3 tools/render.py v2.0.0 --compare v1.0.0
#   -> also: versions/v2.0.0/generated/vs-v1.0.0.svg (both, stacked)
```

Currently generates: an XKB `.xkb_symbols` block (Linux), and SVG
keyboard diagrams. Does **not** yet generate a Windows `.klc` — that's
unbuilt future work (see `versions/v2.0.0/notes.md`, "Known gaps").

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
