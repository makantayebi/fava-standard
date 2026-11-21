# v0.0.6 — ی disambiguated into two keys, یْ added for the /j/ consonant

## The problem

ی has always done double duty in Persian spelling:

- The vowel **/i/** — ب**ی**ت (bit "house"/beet-sound), **س**ی (si
  "thirty"), ش**ی**ت (sheet-sound words) — by far the common case.
- Word-initially in a handful of loanwords and names, the consonant
  **/j/** — **ی**ل (Yale), **ی**من (Yemen), **ی**ورک (York) — the
  glide that starts the English word "yes."

Nothing in the spelling tells a reader which one applies; you have to
already know the word. This is the exact same shape of problem that
motivated the وْ disambiguation in `v0.0.4`/`v0.0.5` (و as consonant
/v/ vs. vowel /uː/) — a single letter carrying two phonemically
unrelated sounds with no written distinction.

## The fix

Same mechanism, same letter-plus-سکون construction as وْ:

- **ی** keeps the vowel reading, /i/, unchanged, on its own key
  (D/AC03). Nothing about typing بیت, سی, شیت changes.
- **یْ** (ی + سکون, one keystroke, two codepoints) is new, and takes
  over the /j/ consonant reading — یْل, یْمن, یْورک. سکون here means
  the same thing it's meant since `v0.0.4`: "read the preceding letter
  as its non-default, consonant/glide value," exactly as it does for و.

یْ is assigned to Y/AD06, which held ARABIC SHADDA (ـّ) through
`v0.0.5`. Shadda moves to shift+ه (AD08/I) instead — not a loss, just
a relocation. (Android's `v0.0.7` fork had already independently added
shift+ه as a *second*, more mnemonic home for shadda — "heh with a
shadda drawn on top" is how native speakers actually describe the
doubled-consonant mark. This version makes that shadda's canonical
home across every target, not just an Android-specific convenience.)

## Implementation

Same mechanism as `v0.0.3`'s shift+Q/W/E and `v0.0.5`'s B:

- **Android**: trivial — `android:keyOutputText="یْ"` directly, no
  special handling needed. (Android's own fork separately decides
  where یْ and shadda actually land on its layout; see
  `layouts/android/`.)
- **Linux/XKB**: needs the Compose mechanism, since a plain XKB key
  still can't emit two codepoints directly. Y's base level is now
  bound to a new PUA trigger keysym (`UF105`), with a matching
  `avayi.XCompose` rule resolving it to یْ. See
  `schema/layout.schema.md`, "Multi-character keys", and
  `tools/render.py`'s `COMPOSE_TRIGGER` table.
