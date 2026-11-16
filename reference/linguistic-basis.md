# Linguistic basis

What kind of project this actually is, in established terms, and what
prior art exists — written so the Fava movement can point to real
linguistic grounding instead of just "this is confusing, let's fix it."

## The classification: Persian script is an impure abjad

In the standard typology of writing systems (Peter T. Daniels,
*The World's Writing Systems*, 1996 — the reference every subsequent
discussion of script types builds on), a script is an **abjad** if its
letters encode consonants and the reader supplies the vowels. Persian's
Perso-Arabic script is specifically an **impure abjad**: ا, و, and ی do
double duty as consonants and as **matres lectionis** — letters that
also mark *long* vowels. Short vowels are relegated to the *harakat*
diacritics (زبر/زیر/پیش), which exist, are linguistically well-defined,
and are almost never actually written outside schoolbooks, the Qur'an,
and dictionaries.

That's not a stylistic quirk — it's the textbook definition of the gap
this project exists to close: **the spelling under-determines the
pronunciation**, and the reader has to already know the word to read it
correctly. [`persian-phonology.md`](persian-phonology.md) and
[`persian-phonemes.yaml`](persian-phonemes.yaml) document the concrete
shape of that gap for Persian specifically (bare `ا` hiding three
different short vowels; و and ی each covering three or more distinct
sounds; four historically-distinct Arabic letters — ذ, ز, ض, ظ — all
collapsing to one Persian phoneme, /z/, while the spelling still
pretends they're different).

Arabic and Hebrew have the identical structural gap, for the identical
reason (both are impure abjads too), which is exactly why **Tashkil**
(Arabic) and **Niqqud** (Hebrew) exist — the same idea as *harakat*,
and they meet the same fate: defined, taught, and essentially unused in
everyday adult writing. Three languages, one script family, one
unsolved problem.

## The correct name for what Fava is

**Fava is an orthographic reform** — the general term (not "script
reform," which specifically means switching the underlying writing
system, e.g. Arabic→Latin). Fava keeps the Perso-Arabic letters; it
reforms the *conventions* for how they're used, aiming to turn Persian
into something closer to a **phonemic orthography** — one where
spelling reliably predicts pronunciation, as opposed to the current
**historical/morphophonemic orthography**, which preserves centuries of
Arabic etymological spelling at the cost of consistent sound-to-letter
mapping.

"Orthographic reform" is a real, populated category with precedent
outside Persian too: the Turkish alphabet reform (1928), the German
*Rechtschreibreform*, Portuguese's 1990 *Acordo Ortográfico*. Fava
belongs in that category, scoped specifically to vowel-explicitness
rather than wholesale script replacement.

## The closest real precedent: Sorani Kurdish

This is the one worth studying in detail, because it's the same script
family solving the same problem, successfully, already:

> "Unlike the Persian alphabet, which is an abjad, Central Kurdish is
> almost a true alphabet in which vowels are given the same treatment
> as consonants." — [Wikipedia: Kurdish alphabets](https://en.wikipedia.org/wiki/Kurdish_alphabets)

Sorani took the Perso-Arabic letter inventory and promoted vowels from
optional diacritics to **full letters**, including inventing new ones
where Persian only has a diacritic: ە for /e/, ۆ for /o/, ێ for /eː/,
alongside fuller use of matres lectionis for the long vowels. The
result reads as recognizably the same script family, but is close to a
true alphabet rather than an abjad. It's a working demonstration that
this exact transformation is achievable without abandoning the script
entirely — which is the core bet Fava is making too, just via a
different mechanism (keyboard-level habitual marking rather than new
letterforms).

## Other reference points

- **Somali orthography (1972)** — adopted the Latin alphabet
  specifically because Arabic-script attempts couldn't represent
  Somali's vowel system adequately. A cautionary precedent in the other
  direction: when an abjad's vowel gap gets bad enough relative to a
  language's phonology, the historical alternative has been abandoning
  the script, not patching it. Fava is betting the patch is enough for
  Persian; worth being explicit that this bet is the crux of the whole
  project.
- **Arabic diacritic restoration** — an active computational-linguistics
  research area: automatically inferring the missing *harakat* from
  context using statistical/neural models. Same underlying task as
  Fava's problem, approached from the NLP side rather than the
  orthography-design side. Directly relevant prior art for
  [`fava-transform`](https://github.com/makantayebi/fava-transform),
  which will need to do the equivalent for Persian.

## Sources

- Daniels, Peter T. & Bright, William (eds.), *The World's Writing
  Systems*, Oxford University Press, 1996 — the standard reference for
  the abjad/abugida/alphabet/syllabary/logography typology.
- [Abjad — Wikipedia](https://en.wikipedia.org/wiki/Abjad)
- [Kurdish alphabets — Wikipedia](https://en.wikipedia.org/wiki/Kurdish_alphabets)
- [Persian phonology — Wikipedia](https://en.wikipedia.org/wiki/Persian_phonology)
