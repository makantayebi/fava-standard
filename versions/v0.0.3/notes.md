# v0.0.3

## Shift+Q/W/E: word-initial short vowels, typed directly

[`persian-phonology.md`](../../reference/persian-phonology.md) documents
that bare `ا` at the start of a word hides one of three different short
vowels (اگر /ʔæ/, اسم /ʔe/, اریب /ʔo/) with no way to tell which from
the spelling. Rather than leave that as a documented problem, shift+Q/W/E
now type the disambiguated form directly, in one keystroke:

| key | base (unshifted) | shift |
|---|---|---|
| Q | ـُ (damma alone) | اُ — ا + damma, for word-initial /ʔo/ |
| W | ـِ (kasra alone) | اِ — ا + kasra, for word-initial /ʔe/ |
| E | ـَ (fatha alone) | اَ — ا + fatha, for word-initial /ʔæ/ |

Each shift value is two codepoints — the same representation
`v0.0.1`'s Windows ligature keys used for "two characters per
keystroke." The difference: this isn't rendering padding, it's the
actual intended output, and it's implementable for real (see
"Implementation" below), not just documented intent.

## Shift+J dropped

J's shift level typed ـ (tatweel/kashida, U+0640) in every version so
far. Not needed; removed. J now behaves like most letter keys — shift
has no distinct effect, same as base.

## ژ freed from B

B and X both typed ژ since `v0.0.2`. X keeps it; B is now unassigned
(`base: null`) — deliberately reserved for a future decision, not
filled with anything yet.

## Implementation: single-keysym compose, not a dead key

Standard XKB can't make one key+shift-level emit two Unicode codepoints
directly — a keysym is always exactly one character. But X11/libxkbcommon
**Compose** files can map a *single* keysym (not just multi-key dead-key
sequences) straight to a multi-character string, and this was verified
empirically before relying on it: a minimal Compose file with

```
<Arabic_fatha> : "اَ"
```

resolves immediately (`XKB_COMPOSE_STATE_COMPOSED` after just the one
keysym — no second keypress needed) to produce the full string.

The catch: if shift+E's keysym were literally `Arabic_fatha` — the same
keysym unshifted E already produces — the compose rule would fire for
*both*, turning bare E into `اَ` too. So shift+Q/W/E are each bound to a
dedicated Private Use Area keysym instead (used purely as a trigger,
never meant to display as itself):

| key | shift keysym (PUA trigger) | composes to |
|---|---|---|
| Q | `UF103` | اُ |
| W | `UF102` | اِ |
| E | `UF101` | اَ |

`tools/render.py` generates both the `.xkb_symbols` (binding shift to
the PUA trigger) and a matching `.XCompose` fragment (mapping each
trigger to its string) from the same `layout.yaml` — see
`generated/avayi.xkb_symbols` and `generated/avayi.XCompose` in this
folder. `ubuntu-keyboard/install.sh` installs the compose fragment into
`~/.XCompose` (user-level, no root needed — simpler than the system XKB
file edits the rest of the layout requires).
