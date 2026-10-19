---
id: TASK-112.03
title: 'MyScribe can be stopped: a stop route, a --stop flag and a Stop button'
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - autostart
  - ux
dependencies: []
references:
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
ordinal: 216000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A headless server has no window to close. Today the only stop is the OS (taskkill /T /F, myscribe_launcher.py:1289-1320) and the app has no shutdown route. What happens to a running job (wait, cancel, or leave it for reconcile to mark interrupted) is a design choice for Robert, possibly an ADR of its own.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Robert has chosen what a stop does to a running job, and that choice is recorded
- [ ] #2 A loopback-only POST stops the server cleanly, so supervisor, watcher and feeds end through the lifespan; a cross-site POST is refused by scribe.guard as today
- [ ] #3 `MyScribe --stop` calls it and falls back to a hard stop after a timeout; a test covers both paths
- [ ] #4 The web UI has a Stop MyScribe action that says what happens to a running job
<!-- AC:END -->
