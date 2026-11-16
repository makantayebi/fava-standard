# Changelog

All notable changes to the Fava layout. Each entry links to the full
writeup in that version's `notes.md`.

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
