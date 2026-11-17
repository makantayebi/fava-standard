# v0.0.5 — B types وْ directly

## What changed

`v0.0.4` resolved و's consonant/vowel ambiguity by repurposing سکون:
type `,` (و) then **B** (سکون) — two keystrokes — to get وْ, the vowel
/uː/ reading, versus bare و alone for the consonant.

Real-world use (and feedback typing on the Android keyboard) showed the
two-keystroke version felt unnecessarily split for something that's
really one decision ("this و is the vowel"), not two. `v0.0.5` collapses
it: **B now types وْ directly**, two codepoints from one keystroke,
same representation `layout.yaml` already uses for `v0.0.3`'s
shift+Q/W/E (ا + mark).

The underlying idea from `v0.0.4` doesn't change — bare و is still the
consonant default, سکون is still retired from its old "no vowel
follows" meaning everywhere else in Fava. Only the keystroke count for
the vowel reading changes, from two presses to one.

## Implementation

Same mechanism as `v0.0.3`'s shift+Q/W/E, extended to a new key:

- **Android**: trivial — `android:keyOutputText="وْ"` directly, no
  special handling. `FavaInputMethodService.onText()` already commits
  whatever string a key carries; this needed zero Kotlin changes.
- **Linux/XKB**: needs the Compose mechanism `v0.0.3` built, since a
  plain XKB key still can't emit two codepoints. B's base level is now
  bound to a new PUA trigger keysym (`UF104`), with a matching
  `avayi.XCompose` rule resolving it to وْ. See
  `schema/layout.schema.md`, "Multi-character keys", and
  `tools/render.py`'s `COMPOSE_TRIGGER` table.
