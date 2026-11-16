# Persian phonology reference

Every letter and diacritic of the Persian script, with its **Persian**
pronunciation (IPA) — not Arabic. This is reference material for future
Fava mapping decisions; it does not itself define any Fava spelling.

**Why this matters, and why it has to be Persian-specific:** Persian
inherited the Arabic script wholesale, including letters for sounds
Arabic has but Persian never did (Persian has no pharyngealized or
pharyngeal consonants at all). Those letters didn't disappear — they
just all collapsed onto whatever native Persian sound was closest, so
several historically-distinct Arabic letters are now pronounced
*identically* in Persian:

| Arabic letters, distinct in Arabic | → single Persian sound |
|---|---|
| ث, س, ص | **/s/** |
| ذ, ز, ض, ظ | **/z/** |
| ت, ط | **/t/** |
| ح, ه | **/h/** |

This is the gap Fava exists to address: the written form still
distinguishes them (for etymology/loanword spelling), but the spoken
language hasn't for centuries.

Sources: [Persian phonology](https://en.wikipedia.org/wiki/Persian_phonology)
and [Persian alphabet](https://en.wikipedia.org/wiki/Persian_alphabet) on
Wikipedia, cross-checked against [Wiktionary's Persian pronunciation
appendix](https://en.wiktionary.org/wiki/Appendix:Persian_pronunciation)
for ی specifically (one source gave it an IPA value that didn't check out
against the others, so it was dropped rather than included on one
source's word — see `persian-phonemes.yaml` notes on `ی`).

## The 32 letters

| Letter | Name | Persian IPA | Arabic IPA (for contrast) | Notes |
|---|---|---|---|---|
| ا | الف (alef) | /ɒː/ (medial/final); glottal-stop carrier word-initially | /ʔ/, /aː/ | |
| آ | الف مد (alef-ye maddeh) | /ɒː/ | /ʔaː/ | used word-initially where bare ا would be ambiguous |
| ب | be | /b/ | /b/ | |
| پ | pe | /p/ | — | not an Arabic letter |
| ت | te | /t/ | /t/ | |
| ث | se | **/s/** | /θ/ | Persian merge target: /s/ |
| ج | jim | /dʒ/ | /dʒ~ɡʲ/ | |
| چ | che | /tʃ/ | — | not an Arabic letter |
| ح | he-ye jimi | **/h/** | /ħ/ | Persian merge target: /h/ |
| خ | khe | /x/ | /x/ | |
| د | dâl | /d/ | /d/ | |
| ذ | zâl | **/z/** | /ð/ | Persian merge target: /z/ |
| ر | re | /ɾ/ | /r/ | |
| ز | ze | /z/ | /z/ | |
| ژ | zhe | /ʒ/ | — | not an Arabic letter |
| س | sin | /s/ | /s/ | |
| ش | shin | /ʃ/ | /ʃ/ | |
| ص | sâd | **/s/** | /sˤ/ | Persian merge target: /s/ |
| ض | zâd | **/z/** | /dˤ/ | Persian merge target: /z/ |
| ط | tâ | **/t/** | /tˤ/ | Persian merge target: /t/ |
| ظ | zâ | **/z/** | /ðˤ/ | Persian merge target: /z/ |
| ع | eyn | /ʔ/, or a plain vowel (/æ/, /ɒ/) depending on position | /ʕ/ | very different from Arabic — Persian has no pharyngeal consonants |
| غ | gheyn | /ɣ/ (merges with ق as [ɣ~ɢ] in colloquial Tehrani speech) | /ɣ/ | |
| ف | fe | /f/ | /f/ | |
| ق | qâf | /q/ (see غ — merges colloquially) | /q/ | |
| ک | kaf | /k/ | /k/ | |
| گ | gaf | /ɡ/ | — | not an Arabic letter |
| ل | lam | /l/ | /l/ | |
| م | mim | /m/ | /m/ | |
| ن | nun | /n/ | /n/ | |
| و | vav | **multi-valued**: /v/ (consonant, word-initial), /uː/ (long vowel), /ow/ or /o/ (word-final/diphthong) | /w/, /uː/ | context-dependent, no single value |
| ه | he-ye do-cheshm | /h/; word-finally sometimes /e/ or /a/ | /h/ | |
| ی | ye | **multi-valued**: /j/ (consonant), /iː/ (long vowel), /ej/ (some word-final contexts) | /j/, /iː/ | |

Not one of the 32 "letters" but structurally similar — a diacritic, not a
base letter:

| Mark | Name | Persian value |
|---|---|---|
| ء | hamze (hamza) | /ʔ/ — seated on ا/و/ی, which then just carry it |

## Short vowels (not written as full letters — diacritics/*harakat*)

| Mark | Name | Persian IPA |
|---|---|---|
| َ (zabar) | فتحه / زبر | /æ/ |
| ِ (zir) | کسره / زیر | /e/ |
| ُ (pish) | ضمه / پیش | /o/ |

Full vowel inventory: short /æ, e, o/ — long /ɒː, iː, uː/.

## Other marks

| Mark | Name | Function |
|---|---|---|
| ّ (tashdid) | تشدید | **not a sound of its own** — doubles (geminates) whatever consonant it sits on |
| ْ (sukun) | سکون | marks the *absence* of any vowel after the consonant |
| ً (tanvine nasb) | تنوین نصب | pronounced **/æn/** in Persian (e.g. فوراً → /foræn/) — used in Arabic-loan adverbs |
| ٍ (tanvine jarr) | تنوین جر | essentially unused in native Persian — Qur'anic/Arabic recitation only |
| ٌ (tanvine rafʿ) | تنوین رفع | rare, essentially unused in everyday Persian |
