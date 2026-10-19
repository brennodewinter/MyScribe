---
id: TASK-112.06
title: >-
  Linux starts MyScribe from a systemd user unit, with the XDG autostart file as
  fallback
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - packaging
  - autostart
  - linux
dependencies:
  - TASK-112.01
  - TASK-112.02
references:
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
ordinal: 219000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Today Linux writes ~/.config/autostart/myscribe.desktop, which nothing supervises. A systemd user unit restarts a crash and logs to the journal. The user manager does not read .profile, so an XDG_DATA_HOME set only in the shell would make the background server open another library. Depends on the Linux open question of ADR-026.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 With a systemd user session, switching on writes ~/.config/systemd/user/myscribe.service and enables it; off disables and removes it
- [ ] #2 Without one, the XDG autostart file is written as today
- [ ] #3 An XDG_DATA_HOME set at registration is written into the unit as Environment=, and a test asserts it
- [ ] #4 The unit restarts only on a crash exit code and stops after five failures in five minutes
<!-- AC:END -->
