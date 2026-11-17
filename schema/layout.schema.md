# `layout.yaml` schema

Each `versions/<version>/layout.yaml` is a complete, standalone, physical
key-by-key definition of the Fava layout at that version. It is the
*only* authoritative place that defines what Fava is — every platform
repo (`windows-keyboard`, `ubuntu-keyboard`, `fava-android-keyboard`,
`ios-keyboard`) implements whatever the latest `layout.yaml` here says,
not the other way around. If a platform file and `layout.yaml` disagree,
`layout.yaml` is right and the platform file is stale.

## Top-level fields

```yaml
version: "0.0.2"          # must match the folder name (versions/v0.0.2/)
name: "Fava (فاوآیی)"
date: 2026-11-16          # YYYY-MM-DD, the date this version was decided
supersedes: "0.0.1"       # previous version's string, or null for the first
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
Windows `.klc` source for v0.0.1 turned out to have its `VK_` *label*
for two keys swapped relative to their true hardware scancode (see
`versions/v0.0.1/notes.md`). Naming keys by physical slot instead of by
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
  emits more than one character per press. Two distinct reasons this
  shows up, handled differently downstream:
  - `v0.0.1`-style **ligature padding**: Windows' literal "space +
    combining mark" workaround, a platform limitation, not a design
    choice. `tools/render.py` can't turn this into a real key binding
    (no single keysym exists for it) and just records it for history.
  - `v0.0.3`-onward **intentional multi-character output**, e.g.
    shift+E typing اَ (ا + fatha) in one keystroke. These *are*
    implementable, via a single-keysym Compose rule rather than a
    normal key binding — see "Multi-character keys" below. Whether a
    given multi-codepoint value is implementable this way depends on
    whether it has an entry in `tools/render.py`'s `COMPOSE_TRIGGER`
    table; add one when you add the key.

  ```yaml
  AD01:                                      # Q
    base: "U+064F"                           # ARABIC DAMMA — one keysym, normal key
    shift: ["U+0627", "U+064F"]               # ا + DAMMA — two codepoints, via Compose
  ```

- `base: null` means the key is deliberately unassigned — reserved for
  a future decision, not "unchanged from the previous version." A key
  *absent* from `keys:` means unchanged; a key present with `base: null`
  means explicitly freed.

## Multi-character keys (Compose, not a dead key)

A keysym is always exactly one character — XKB has no way to bind one
key+shift-level to two codepoints directly. Instead, that key's shift
level is bound to a dedicated Private Use Area (PUA) keysym that's
never meant to be seen on its own, and a matching **Compose** rule maps
that single keysym straight to the real multi-character string. This
was verified empirically (not just assumed) before relying on it: X11
Compose files resolve a single keysym to a full string immediately,
no second keypress needed, same mechanism dead keys use but triggered
by one keysym instead of two.

`tools/render.py`'s `COMPOSE_TRIGGER` dict assigns each such key's PUA
codepoint (`AD01`→`UF103`, `AD02`→`UF102`, `AD03`→`UF101` so far — pick
any unused PUA codepoint when adding more, just don't reuse one). The
tool then emits both `avayi.xkb_symbols` (binding the trigger) and
`avayi.XCompose` (mapping it to the string) from the same `layout.yaml`
— they have to be installed together for the key to actually work.

## Rendering a version

```bash
python3 tools/render.py v0.0.2
```
writes `versions/v0.0.2/generated/avayi.xkb_symbols` (drop-in for
`ubuntu-keyboard/symbols/avayi.xkb_symbols`) and SVG keyboard diagrams
into `versions/v0.0.2/generated/`. See `tools/render.py --help`.
