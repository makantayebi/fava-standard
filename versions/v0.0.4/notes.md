# v0.0.4 — splitting و's two sounds

## The problem

و does two unrelated jobs in Persian with no written distinction:
consonant /v/ (ورزش، واقعی) and the long vowel /uː/ (دور، نور، تو).
[`persian-phonemes.yaml`](../../reference/persian-phonemes.yaml) already
listed و as multi-valued; this version is the first concrete fix.

## Candidates considered and rejected

Explored first: borrowing a dedicated letter from a sibling Perso-Arabic
script that already solved this — Uyghur/Kazakh/Kyrgyz/Azerbaijani all
split waw into three atomic letters (ۋ consonant, ۇ /uː/, ۆ /oː/).
Rejected: reads as a Turkic import to an Iranian eye, not a native
Persian device, even though the underlying method (modify a base letter
with a mark) is the same method that produced پ/چ/ژ/گ historically.

Then checked **doubling the letter** (وو = /uː/, matching how Sorani
Kurdish writes the same vowel) and **damma directly on the vav** (وُ).
Both rejected on the same ground: real collisions against real, common
existing words.
- وو: داوود (a common name) and طاووس ("peacock") already contain a
  genuine consonant-و + vowel-و sequence that is *not* a single long
  /uː/ — a blanket "وو = long u" rule would misparse them.
- وُ: already has a standard, existing reading as consonant /v/ + the
  short vowel /o/ (an ordinary damma on an ordinary consonant) — this
  is a direct, load-bearing collision, not a rare edge case.

Also explored a family of genuinely unused native Arabic marks from the
Qur'anic recitation-annotation block (U+0656–U+065F — inverted damma,
dot-below, two small-v variants). All render correctly (real anchor
data, confirmed by rendering them) and have zero real-word collision.
Rejected only because they're obscure typesetting marks almost no
Iranian reader has ever seen, even though they're not Turkic imports.

## The resolution: retire and repurpose سکون

سکون (sukun, U+0652) already has a real, universal meaning — "no vowel
follows this consonant" — but per
[`persian-phonology.md`](../../reference/persian-phonology.md), harakat
in general (sukun included) are "almost never actually written outside
schoolbooks, the Qur'an, and dictionaries." Its old job has near-zero
real-world footprint in actual written Persian, which makes it close to
redundant in practice — so this version **retires sukun's old meaning
everywhere in Fava** and gives it one new, exclusive job: placed after
و, it marks that و as the vowel /uː/, not the consonant.

Checked for collisions the same way as the rejected options above: since
sukun is barely ever written in real text to begin with, there's no body
of existing داوود-style real words using وْ in its old sense to collide
with. مثال: داوود respells as **دآووْد** — د(d) + آ(ɒː) + و(v, unmarked
consonant) + وْ(u, the new rule) + د(d) = /dɒːvud/, matching the real
pronunciation with every sound now explicit.

This also has a legibility edge the Qur'anic marks didn't: sukun is at
least named and taught in school, even though it's rarely *written* —
unlike U+065A–U+065F, which are specialist marks almost nobody has seen
rendered at all.

**Known trade-off, accepted deliberately, not an oversight:** if some
other word ever needs an explicit "no vowel follows" marker for its own
disambiguation, that tool is gone — sukun now means one specific thing
tied to و, full stop.

## Keyboard placement

Assigned to **B** (`AB05`) — freed up in `v0.0.3` specifically pending a
future decision, and this is it. `B` emits the bare sukun mark alone,
the same pattern Q/W/E already use for their own bare marks: type و
(the `,` key) first, then `B` — text shaping stacks the mark onto the
preceding glyph on its own, no Compose trick needed (unlike shift+Q/W/E
in `v0.0.3`, which genuinely needed one because they emit *two*
characters from *one* keystroke; this is one character from one
keystroke, typed after another single-character keystroke).
