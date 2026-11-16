# Changelog

All notable changes to the Fava layout. Each entry links to the full
writeup in that version's `notes.md`.

## v2.0.0 — 2026-11-16

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
  true v1.0.0 Windows file does. v2.0.0 does not restore v1.0.0's Y/Z;
  it knowingly builds on top of the swapped state. Full story in
  [`versions/v2.0.0/notes.md`](versions/v2.0.0/notes.md).

## v1.0.0 — 2021-10-13

Original layout, authored in Microsoft Keyboard Layout Creator, shipped
as the `PE5` Windows installer. Historical baseline.

Details, including a `VK_`-label quirk in the source `.klc` file, in
[`versions/v1.0.0/notes.md`](versions/v1.0.0/notes.md).
