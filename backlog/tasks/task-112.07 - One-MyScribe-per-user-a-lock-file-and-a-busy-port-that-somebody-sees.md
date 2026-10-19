---
id: TASK-112.07
title: 'One MyScribe per user: a lock file, and a busy port that somebody sees'
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
ordinal: 220000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Launch.prepare probes /health and then binds the port (myscribe_launcher.py:1536-1553), which leaves a race between a login item and a start by hand. A busy port in a headless start is only a log line nobody reads.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An exclusive lock in the home is taken before the health probe; a second start that finds it opens the browser and exits 0
- [ ] #2 A test starts two launchers at once and only one serves
- [ ] #3 A busy port in a headless start is written to launcher.log and shown at the next start by hand
<!-- AC:END -->
