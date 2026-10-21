---
id: TASK-112.09
title: >-
  Window Quit, Ctrl+C and SIGTERM stop MyScribe through the stop route, so every
  stop requeues and no runner outlives the app
status: To Do
assignee: []
created_date: '2026-10-21 18:03'
labels:
  - autostart
  - packaging
dependencies:
  - TASK-112.03
references:
  - >-
    docs/adr/ADR-028-a-deliberate-stop-puts-the-running-job-back-at-the-front-of-the-queue.md
parent_task_id: TASK-112
ordinal: 226000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
ADR-028 (answered by Robert on 2026-10-21): every stop goes through the stop route. Today only POST /api/shutdown, the Settings button and MyScribe --stop requeue the running job. Window Quit and a POSIX SIGTERM end the app through AppProcess.stop: on Windows taskkill ends the runner and reconcile marks its job interrupted; on macOS and Linux the runner has a session of its own and runs on as an orphan (measured in WSL on 2026-10-21: it wrote done 13 s after the app had gone), holding the GPU with no app to show it. Ctrl+C on a headless launcher takes the same path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Window Quit and a SIGTERM to the launcher call the stop route first and wait for the app's pid, with AppProcess.stop as the fallback after a timeout
- [ ] #2 A job running at that moment is queued again at the front, on Windows, macOS and Linux; a test covers each door
- [ ] #3 On macOS and Linux no runner outlives the app after a Quit; shown in WSL or on a Mac with a slow fake job
- [ ] #4 The window and the console say what happens to the running job before and after the stop
<!-- AC:END -->
