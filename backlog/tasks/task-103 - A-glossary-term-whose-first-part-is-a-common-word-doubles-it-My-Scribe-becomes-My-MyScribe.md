---
id: TASK-103
title: >-
  A glossary term whose first part is a common word doubles it: My Scribe
  becomes My MyScribe
status: Done
assignee: []
created_date: '2026-10-04 07:07'
updated_date: '2026-10-12 03:23'
labels:
  - transcription
  - bug
dependencies: []
priority: low
ordinal: 185000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found while building TASK-102.04 (measured 2026-10-04): corrections_for with a user term 'MyScribe' on the words 'My Scribe' corrects only the one-word window 'Scribe' (fuzz.ratio 85.7 against 'MyScribe', at the threshold) and leaves 'My', so the transcript reads 'My MyScribe'. 'Mi Scribe' goes right (both words replaced), 'My Scribe' does not, which points at how overlapping windows are chosen, not at the threshold alone. Any user term whose first part is an ordinary word can hit this.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A failing test shows 'My Scribe' with the user term 'MyScribe' corrected to one 'MyScribe' (the two-word window wins), red first
- [x] #2 The existing glossary tests (the 'met Marieke' guard against deleting words included) stay green
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Find why a term already spelled across two words was corrected again inside (MyMyScribe, NotebookLMLM).
2. Make an already-spelled window claim its words; require both edge words of a multi-word window to be pieces of the term (TASK-110).
3. Measure every rule change against main on deletion, compound, split and name-pair sweeps; adversarial review per round until no damage remains that main does not do.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause (2026-10-11): the task's own example ('My Scribe' -> 'My MyScribe') was already green on the stored word shape. The real bug: a window already spelled the way the glossary wants it was skipped with `continue`, so a sub-window got its own correction: ' My'+'Scribe' -> 'MyMyScribe', 'Notebook'+'LM' -> 'NotebookLMLM', 'J J Smithson'. Fix: such a window claims its words and writes nothing; only a fuzzy correction over more words that extends the claimed term (accents aside, canonical or the matched variant) and whose last word is spelled as the rest of the term (PAST_CLAIM_FLOOR 80) may beat it.

Done together with TASK-110 in one change to corrections_for; the evidence table is in TASK-110's notes. 47 tests in tests/test_glossary.py fail against main's glossary.py (swapped in via a pytest plugin) and pass on the branch: 151 passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
A term already spelled across two words claims them, so its parts are no longer corrected again ('MyMyScribe', 'NotebookLMLM'). Verified: tests/test_glossary.py 151 passed, 47 of them red against main's glossary.py; the twelve glossary-related test files green one by one.
<!-- SECTION:FINAL_SUMMARY:END -->
