---
id: TASK-112.08
title: >-
  Decide whether a crashed server restarts on Windows, and whether MyScribe gets
  a tray icon
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - autostart
dependencies: []
references:
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
priority: low
ordinal: 221000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
ADR-026 leaves two choices open. Restart after a crash on Windows means a per-user scheduled task instead of the Run value, with defaults that must all be overridden (battery, a 72-hour limit, below-normal priority) and unverified rights for a standard user. A tray icon makes running and stopping visible, but pystray 0.19.5 (2023, LGPL-3.0) breaks the standard-library-only rule of ADR-011 for the launcher. Each choice that goes ahead gets its own ADR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Robert has answered both, with the consequences of each option in front of him
- [ ] #2 Each yes has a Proposed ADR and a task; each no is recorded in this task
<!-- AC:END -->
