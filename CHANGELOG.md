# Changelog

All notable changes to the Fava layout. Each entry links to the full
writeup in that version's `notes.md`.

## v0.0.5 — 2026-11-18

- B now types **وْ** directly — one keystroke, two codepoints — instead
  of requiring `,` (و) then B (سکون) as two separate presses. Same
  disambiguation from `v0.0.4`, just collapsed into one key. Uses the
  same Compose mechanism `v0.0.3` built for shift+Q/W/E, extended to a
  new trigger. See
  [`versions/v0.0.5/notes.md`](versions/v0.0.5/notes.md).

## v0.0.4 — 2026-11-17

- Split و's two unrelated sounds (consonant /v/ vs. vowel /uː/): bare و
  stays the consonant default, و followed by **B** (سکون) now explicitly
  marks the vowel reading — دآووْد for داوود, for example.
- سکون's old meaning ("no vowel follows") is retired everywhere else in
  Fava — deliberately, since it was barely ever written in real Persian
  anyway. Several other options (borrowed Uyghur-style letters, doubled
  وو, damma-on-vav, obscure Quranic marks) were explored and rejected,
  mostly for colliding with real existing words (داوود، طاووس، مسؤول) —
  full reasoning in
  [`versions/v0.0.4/notes.md`](versions/v0.0.4/notes.md).
- Fills the **B** key, freed in `v0.0.3` pending exactly this kind of
  decision.

## v0.0.3 — 2026-11-17

- Shift+Q/W/E now type the disambiguated word-initial short vowel
  (ا + the mark — اُ/اِ/اَ) in one keystroke, directly addressing the
  bare-ا ambiguity in [`persian-phonology.md`](reference/persian-phonology.md).
  Implemented via a single-keysym Compose rule, not a dead key — see
  [`versions/v0.0.3/notes.md`](versions/v0.0.3/notes.md) for how, and
  why a normal `.xkb_symbols` key binding can't do this directly.
- Shift+J's tatweel dropped — unneeded.
- ژ freed from B (X keeps it alone); B left explicitly unassigned
  (`base: null`) — filled in `v0.0.4`, see below.

## v0.0.2 — 2026-11-16

Developed while building the Ubuntu/Linux implementation and a
side-by-side diagram comparing it against the original Windows file.

- Dropped the Windows-only "ligature padding" (Q/W/E/D/`,` used to type
  a space or base letter before a combining mark); bare combining marks
  are used instead.
- Q/W/E rotated: Q=damma, W=kasra, E=fatha (was Q=fatha, W=damma,
  E=kasra).
- Y reassigned to shadda (ـّ).
- D reassigned to yeh (ی) — where yeh ended up after leaving Y.
- X reassigned to jeh (ژ), duplicating B.
- `,` (comma) reassigned to waw (و).
- **Also documented, not changed:** an unintentional swap of physical Y
  and Z discovered during this work — the Linux port had carried ZWNJ
  on Z and yeh on Y since it was first created, the reverse of what the
  true v0.0.1 Windows file does. v0.0.2 does not restore v0.0.1's Y/Z;
  it knowingly builds on top of the swapped state. Full story in
  [`versions/v0.0.2/notes.md`](versions/v0.0.2/notes.md).

## v0.0.1 — 2021-10-13

Original layout, authored in Microsoft Keyboard Layout Creator, shipped
as the `PE5` Windows installer. Historical baseline.

Details, including a `VK_`-label quirk in the source `.klc` file, in
[`versions/v0.0.1/notes.md`](versions/v0.0.1/notes.md).
