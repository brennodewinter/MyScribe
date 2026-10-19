---
id: TASK-112.04
title: An update or uninstall on Windows stops a running MyScribe first
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - packaging
  - autostart
dependencies:
  - TASK-112.03
references:
  - docs/reports/2026-10-19-background-server-research.md
  - packaging/windows/myscribe.iss
parent_task_id: TASK-112
ordinal: 217000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
myscribe.iss has no [UninstallRun] stop and no PrepareToInstall stop. A running headless server keeps serving the old code after an update, and its python.exe lives outside {app}, where Restart Manager does not look. The first update still finds the old MyScribe.exe without --stop, so the installer code calls the stop route itself with taskkill as fallback.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An update while MyScribe runs stops it, installs, and starts it headless again when the login item is on
- [ ] #2 An uninstall while MyScribe runs stops it before files are removed, and removes the Run value as today
- [ ] #3 Both work against a server started by an older version that has no --stop
- [ ] #4 A real install over a running 0.8.x on Windows shows it, with the install log
<!-- AC:END -->
