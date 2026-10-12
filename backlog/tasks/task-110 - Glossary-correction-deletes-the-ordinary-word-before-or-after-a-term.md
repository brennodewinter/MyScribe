---
id: TASK-110
title: Glossary correction deletes the ordinary word before or after a term
status: Done
assignee: []
created_date: '2026-10-11 20:08'
updated_date: '2026-10-12 03:23'
labels:
  - glossary
  - bug
  - data-loss
dependencies: []
priority: high
ordinal: 211000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found 2026-10-11 by the adversarial review of TASK-103 (workflow wf_2f95b4bc-624, matrix of 7,381 term x neighbour x spelling cases, stored word shape). On main (v0.8.5) corrections_for lets a two-word window that merely contains a term replace both words: the window scores at or above FUZZY_THRESHOLD 85 (e.g. 'in amsterdam' vs 'Amsterdam' 90, 'Amsterdam en' 85.7, 'NotebookLM is' 87.0), so the term is written into one word and the other is emptied. Measured on main: the word AFTER a term deleted in 280 cases, the word BEFORE a term in 1,353 (781 of them with the term spelled exactly). Examples: 'Ik woon in Amsterdam.' -> 'Ik woon Amsterdam.'; 'Ik sprak met Marieke Vermeulen gisteren.' -> 'Ik sprak Marieke Vermeulen gisteren.'; 'Dat is Zaphod Beeblebrox.' -> 'Dat Zaphod Beeblebrox.'. The module docstring's 'met Marieke' guard only holds because that pair scores 77.8. Affects every transcript corrected against a glossary with ordinary names; corrections are stored rows, so existing transcripts may already have lost words (not measured on real data).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A test matrix of terms x neighbours (before and after) x spellings deletes no ordinary word, red first on main
- [x] #2 Split compounds still join (Git Hub, Notebook LM, My Scribe, Mi Scribe, Jan sen) including when the first half is itself a term
- [x] #3 Say whether stored corrections in an existing library can be found and undone, and how (not done here without Robert)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Find why a term already spelled across two words was corrected again inside (MyMyScribe, NotebookLMLM).
2. Make an already-spelled window claim its words; require both edge words of a multi-word window to be pieces of the term (TASK-110).
3. Measure every rule change against main on deletion, compound, split and name-pair sweeps; adversarial review per round until no damage remains that main does not do.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Rule (scribe/glossary.py module docstring): a multi-word window is a candidate only if both edge words are pieces of the term - anchored cut, the leftover spelled within EDGE_WORD_FLOOR 50 or the same metaphone, never a word with a vowel for a leftover without one (accents count as vowels). Already-spelled windows claim their words (TASK-103); a correction may beat a claim only if fuzzy, extending the claimed term, and its last word scores >= PAST_CLAIM_FLOOR 80 against the rest.

Measured 2026-10-12, main (HEAD cd82d29) vs branch, eight rounds of adversarial review (scratch harnesses, not in the repo):
| harness | main | branch |
|---|---|---|
| deletion matrix 7,381: neighbour word lost / exact spelling respelled | 1,633 / 1,919 | 0 / 0 |
| deletion matrix 45,315: sentences with a lost word | 6,181 | 677 (all also lost on main) |
| compound matrix 3,751: right | 2,890 | 3,630 |
| compounds 27,648: stored / bare / glued right | 7,296 / 1,596 / 3,996 | 7,776 / 9,216 / 9,216, 0 regressions |
| name-extension pairs 142,896 (Jan/Jans, Kim/Kimberly ...): damaged | 7,549 | 365, 0 where main is clean |
| name-substitution pairs 11,664 (Marie/Maria ...): damaged | 11,280 | 44, 0 where main is clean |
| function words next to terms 648: lost a word | 54 | 42 |
| patronymic pairs 1,320: words lost | 184 | 160, 0 where main keeps |
| exact splits 4,220 right | 4,220 | 4,220 |
| accent/variant probes 26,647: fewer words than main | - | 0 |

Accepted recall cost (output == input, nothing lost): 111 of 21,425 sound-alike splits left as Whisper wrote them ('Voo goon'); past-claim joins 152/212 vs 174 ('My Scrybe'); a one-letter piece written with a vowel stays next to the term ('Ze Sinterklaas', 164 of 2,512 probes). Pre-existing and not fixed: 'Henk een boek' -> 'Henken boek' with Henken listed (een/den/men 80 against 'en'); a user-listed variant like 'Sophie Anne' is taken at its word; TASK-111 (het -> Hetty).

AC #3, stored corrections: word.text is never overwritten (ADR-003); a deleted word is a non-manual word_correction row with corrected=''. glossary.store replaces every non-manual row of a run, so after this release the Settings action that re-runs corrections on the whole library (one `correct` job per transcribed media) rebuilds each layer under the new rules and the lost words come back; hand-made (rule='manual') rows are kept. Which stored rows were wrong can be found by diffing a run's layer before and after that re-run. Not run on a real library: that needs Robert.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
corrections_for no longer deletes the ordinary word next to a term: both edge words of a multi-word window must be pieces of the term. Lost words in the 7,381-case matrix 1,633 -> 0, in 45,315 sentences 6,181 -> 677 (all also lost on main); compounds and splits still join. AC #3: re-running corrections on the library rebuilds stored layers; not run on a real library.
<!-- SECTION:FINAL_SUMMARY:END -->
