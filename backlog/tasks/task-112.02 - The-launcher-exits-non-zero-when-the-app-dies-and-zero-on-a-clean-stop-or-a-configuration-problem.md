---
id: TASK-112.02
title: >-
  The launcher exits non-zero when the app dies, and zero on a clean stop or a
  configuration problem
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - packaging
  - autostart
dependencies: []
references:
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
ordinal: 215000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`run_headless` returns 0 also when the app child dies (myscribe_launcher.py:2213-2221), and 1 for a missing library drive or a busy port. A supervising mechanism (launchd KeepAlive, systemd Restart=on-failure) would then never restart a crash, or retry a failed multi-GB sync every few seconds. One exit-code contract fixes both.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A dead app child ends the launcher with its own documented non-zero code; a test kills the child and asserts it
- [ ] #2 A clean stop, another instance already serving, and a configuration problem (no library drive, port busy, offline sync) end with 0, and each is written to launcher.log
- [ ] #3 Errors printed before a Layout exists (main, :2947-2970) also reach a log file in a headless start
<!-- AC:END -->
