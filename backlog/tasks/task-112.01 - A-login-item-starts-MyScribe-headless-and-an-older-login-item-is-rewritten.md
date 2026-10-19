---
id: TASK-112.01
title: 'A login item starts MyScribe headless, and an older login item is rewritten'
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - packaging
  - autostart
dependencies: []
references:
  - >-
    docs/adr/ADR-026-myscribe-runs-in-the-background-as-a-per-user-login-item-started-headless-not-as-an-operating-system-service.md
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
ordinal: 214000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Today `start_command` (scribe/autostart.py:308-318) registers `--at-login --no-browser`, and the launcher still opens its Tk window (myscribe_launcher.py:2957). With `--headless` added no window and no console appear. Items written by earlier versions carry the old command and must be brought up to date. Waits for ADR-026.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The command registered on Windows, macOS and Linux carries `--headless`, and a test per OS asserts it
- [ ] #2 At start, a login item whose command differs from the current one is rewritten; one the user switched off stays off
- [ ] #3 Settings says that MyScribe then runs without a window and how to open it (the Start menu entry or localhost:4242)
- [ ] #4 Robert logs out and in on Windows: no window, /health answers; switched off, out and in: nothing answers
<!-- AC:END -->
