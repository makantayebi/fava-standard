# `layout.yaml` schema

Each `versions/<version>/layout.yaml` is a complete, standalone, physical
key-by-key definition of the Fava layout at that version. It is the
*only* authoritative place that defines what Fava is — every platform
repo (`windows-keyboard`, `ubuntu-keyboard`, `android-keyboard`,
`ios-keyboard`) implements whatever the latest `layout.yaml` here says,
not the other way around. If a platform file and `layout.yaml` disagree,
`layout.yaml` is right and the platform file is stale.

## Top-level fields

```yaml
version: "2.0.0"          # must match the folder name (versions/v2.0.0/)
name: "Fava (فاوآیی)"
date: 2026-11-16          # YYYY-MM-DD, the date this version was decided
supersedes: "1.0.0"       # previous version's string, or null for the first
summary: >
  One or two sentences: what changed and why, for someone skimming
  CHANGELOG.md. Full detail goes in this version's notes.md.
keys:
  <PHYSICAL_KEY>: { ... }
  ...
```

## Physical key names

Keys are named by physical position, not by whatever letter happens to
be printed on a US keyboard there — this is deliberate, because the
Windows `.klc` source for v1.0.0 turned out to have its `VK_` *label*
for two keys swapped relative to their true hardware scancode (see
`versions/v1.0.0/notes.md`). Naming keys by physical slot instead of by
label makes that class of bug impossible to re-introduce here.

Names follow the standard Linux/XKB evdev naming (also exactly what
`ubuntu-keyboard`'s `.xkb_symbols` file uses, so translating between the
two is direct):

| Row | Keys |
|---|---|
| number row | `TLDE` (the `` ` `` key, left of 1), `AE01`..`AE10` (1..0), `AE11` (`-`), `AE12` (`=`) |
| QWERTY row | `AD01`..`AD12` (Q..P, `[`, `]`), `BKSL` (`\`, to the right of `]` on ANSI) |
| ASDF row | `AC01`..`AC11` (A..L, `;`, `'`) |
| ZXCV row | `AB01`..`AB10` (Z..M, `,`, `.`, `/`) |
| other | `LSGT` (ISO 102nd key), `KPDL` (numpad decimal), `SPCE` (space bar) |

A key absent from `keys:` is unchanged from the version it `supersedes`
— you only need to list what actually changed, plus (for the very first
version) everything.

## Per-key value

```yaml
keys:
  AD01:                        # Q
    base: "U+064F"             # ARABIC DAMMA (ُ)
    shift: "U+064F"            # optional — omit entirely to mean "same as base"
  AD05:                        # T
    base: "U+0641"             # ARABIC LETTER FEH (ف)
    shift: "U+060C"            # ARABIC COMMA (،)
```

- Always a Unicode codepoint (`U+XXXX`), **never a literal character** —
  combining marks and visually-similar lookalikes (e.g. ي vs ی) are
  exactly the kind of thing that's unreadable at a glance and easy to
  paste wrong; `U+XXXX` is unambiguous and grep-able. Put the literal
  character and its Unicode name in a trailing comment for humans.
- `shift` may be omitted, meaning "this key has no distinct shifted
  output" (CapsLock also has no effect, matching the layout's
  shift-lock-across-everything behavior — see `README.md`).
- A value may be a **list** of codepoints instead of one, for a key that
  historically emitted more than one character per press (only used in
  `v1.0.0`, to record Windows' literal "space + combining mark" ligature
  keys — a platform-specific padding trick later versions don't need,
  since modern text shaping attaches a bare combining mark to the
  previous glyph on its own). Example:

  ```yaml
  AD01:                          # Q, in v1.0.0 only
    base: ["U+0020", "U+064E"]   # SPACE + ARABIC FATHA
  ```

## Rendering a version

```bash
python3 tools/render.py v2.0.0
```
writes `versions/v2.0.0/generated/avayi.xkb_symbols` (drop-in for
`ubuntu-keyboard/symbols/avayi.xkb_symbols`) and SVG keyboard diagrams
into `versions/v2.0.0/generated/`. See `tools/render.py --help`.
