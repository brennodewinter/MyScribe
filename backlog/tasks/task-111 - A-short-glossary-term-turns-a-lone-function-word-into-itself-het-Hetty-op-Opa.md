---
id: TASK-111
title: >-
  A short glossary term turns a lone function word into itself (het -> Hetty, op
  -> Opa)
status: To Do
assignee: []
created_date: '2026-10-11 20:59'
labels:
  - glossary
  - bug
  - data-loss
dependencies: []
priority: high
ordinal: 212000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found 2026-10-11 by the round-3 deletion review of TASK-103/110 (scratchpad task103/skeptic_del/dm.py, 45,315 sentences): with a short term in the glossary, the single-word phonetic rule respells an unrelated function word anywhere in a sentence: het -> Hetty, op -> Opa, in -> Ina, at 0.9 confidence. 376 of the 647 word losses left on the TASK-110 branch are this class; it is the same on main (pre-existing) and outside the multi-word window logic TASK-110 changes. Also recorded there, still open after TASK-110: a listed longer name completed by 'en' (Niels en -> Nielsen, Peter en -> Petersen) and a middle word inside a multi-word window ('Marieke en Vermeulen').
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A test over common Dutch and English function words with short glossary terms shows none respelled, red first
- [ ] #2 The middle-word and name+en classes are fixed here or have their own decision recorded
<!-- AC:END -->
