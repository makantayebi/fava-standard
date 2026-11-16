# v2.0.0 — the Fava redesign

## Dropping ligature padding

v1.0.0's Q/W/E/D/`,` keys each typed two characters on Windows (a space
or base letter, then a combining mark) — a workaround for how Windows
rendered a floating combining mark with nothing to attach to. Modern
text shaping doesn't need that: a bare combining mark attaches to the
previous glyph directly. So here those keys just emit the mark alone.
This is a platform-capability difference, not a design opinion — if a
future platform ever needs the padding again, re-derive it from the
ligature lists already preserved in `v1.0.0/layout.yaml`, don't treat
losing it as a regression.

## The Y/Z lineage (reconstructed, not released as its own version)

This needs to be told in three steps, because what actually happened
doesn't collapse into one clean diff against v1.0.0:

1. **v1.0.0 (true Windows behavior):** physical **Y** → ZWNJ, physical
   **Z** → ی. (See `../v1.0.0/notes.md` — the `.klc` file's own `VK_`
   labels say the opposite, but scancode is what's authoritative.)
2. **Undocumented, never tagged:** when this layout was first ported to
   Linux, the port read the `.klc` file's `VK_` *labels* at face value
   instead of its scancodes, so it reproduced the labels' claim rather
   than the true behavior — physical **Y** got ی, physical **Z** got
   ZWNJ. Nobody designed this; it was a transcription mistake, and it
   went unnoticed for a while because the Linux layout was internally
   consistent on its own terms, and nothing was ever tested key-for-key
   against the real Windows installer.
3. **v2.0.0 (this version):** while building a diagram that rendered
   both platforms side by side, the mismatch became visible and got
   traced to its root cause (above). Rather than silently "fixing" Y/Z
   back to the v1.0.0 values, the decision was to keep iterating on top
   of the state the Linux layout was already in — **Y** was
   deliberately reassigned again, to shadda (ـّ), and **Z** was left as
   ZWNJ. So v2.0.0 does *not* restore v1.0.0's Y/Z assignment; it
   knowingly builds on the accidental one.

**Net effect:** ZWNJ has lived on physical Z since the undocumented
intermediate step, not on Y as v1.0.0 intended. ی moved off Y entirely
and now lives on **D** (see below), so it didn't get lost, just
relocated — twice.

## Other key reassignments made this version

- **Q/W/E rotated**: `fatha→damma→kasra→fatha` (was Q=fatha, W=damma,
  E=kasra in v1.0.0; now Q=damma, W=kasra, E=fatha).
- **D**: was a یْ (yeh+sukun) ligature in v1.0.0 → now bare ی (yeh).
  This is where yeh ended up after leaving Y (see above).
- **X**: was و (waw) in v1.0.0 → now ژ (jeh), duplicating what's
  already on B. Deliberate, not a conflict to resolve.
- **`,` (comma)**: was a وْ (waw+sukun) ligature in v1.0.0 → now bare و
  (waw).

## Known gaps

- `SPCE` is specified here as plain space, but the current
  `ubuntu-keyboard` `.xkb_symbols` file doesn't declare a `<SPCE>` key
  at all — it just inherits the base layout's default, which happens to
  already be space. Harmless today; worth adding explicitly if a future
  version ever wants SPCE to do something else.
- No Windows `.klc` has been generated for this version yet —
  `windows-keyboard` still ships v1.0.0. `tools/render.py` only emits
  `.xkb_symbols` and diagrams so far; generating an updated `.klc` from
  `layout.yaml` is unbuilt future work.
