# v1.0.0 — original Windows baseline

The first Fava layout, authored in Microsoft Keyboard Layout Creator
(MSKLC) 1.4 as `Farsi-Avayi.klc` (internal KBD name `PE4`, description
"فارسی فونتیک"), and shipped as a compiled installer (`PE5`) on
2021-10-13. This version is a historical record of exactly what that
file does — it is not edited going forward.

## The Y/Z quirk

The source `.klc` file's `LAYOUT` table has a row for every physical
key, identified by **scancode** (`SC`) — that's what Windows actually
dispatches on — plus a `VK_` column that's just a descriptive label.
Two of those labels are wrong:

```
15   Z    ...   200C   ...   // scancode 0x15 is physically the Y key
2c   Y    ...   06CC   ...   // scancode 0x2c is physically the Z key
```

Scancode `0x15` is, on every standard keyboard, the **Y** key. Scancode
`0x2C` is the **Z** key. So despite the labels, what this layout
*actually does* when compiled and run is: pressing **Y** produces ZWNJ,
and pressing **Z** produces ی. Every other letter key's label matches
its true scancode position correctly — this looks like a one-off
copy/paste slip while authoring the file in MSKLC's grid UI, not a
deliberate choice.

This is exactly why `layout.yaml` keys are named by physical slot
(`AD06`, `AB01`, ...) instead of by the label printed on a US keyboard:
it makes this entire class of mistake structurally impossible to repeat
here, even though the historical source file has it.

## Ligature keys (Q, W, E, D, `,`)

Five keys are recorded here as a **list** of two codepoints instead of
one. On Windows, pressing one of these keys types *two characters*:
a literal space followed by a combining mark (Q/W/E), or a base letter
followed by a combining sukun (D, `,`). This was a workaround for how
older Windows text rendering handled a floating combining mark with no
preceding base character — MSKLC's "LIGATURE" mechanism, not a true
dead key.

Later versions don't carry this padding forward: modern text shaping
(HarfBuzz/Pango, used by every current Linux/Android/iOS text stack)
attaches a bare combining mark to whatever precedes it without needing
a placeholder. See `../v2.0.0/notes.md`.
