---
id: TASK-113.02
title: >-
  A failed install says what failed: no internet advice for a non-network error,
  and the Setup button does not pretend MyScribe starts
status: To Do
assignee: []
created_date: '2026-10-19 18:15'
labels:
  - packaging
  - ux
  - bug
dependencies: []
references:
  - 'https://github.com/rvdbreemen/MyScribe/issues/16'
  - packaging/launcher/myscribe_launcher.py
parent_task_id: TASK-113
ordinal: 224000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue 16 shows two misleading lines. After the uv failure the window says `Check the internet connection and start MyScribe again`, but the error was a file system one (myscribe_launcher.py:1571). Then the Setup button (open_setup, :2832) ran `setup_plan` against an env python that does not exist and reported `[WinError 2] ... MyScribe starts anyway` (:1899), while nothing could start.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The internet advice appears only when the uv output points at the network (download, DNS, TLS, proxy); otherwise the line says the install failed on this computer and points at the log
- [ ] #2 The Setup button with no env python says the speech engine is not installed yet and offers no sitting; it never says MyScribe starts anyway
- [ ] #3 Tests cover both messages, red before and green after
<!-- AC:END -->
