---
id: TASK-112.05
title: 'The macOS LaunchAgent starts the binary itself, headless, with its own log'
status: To Do
assignee: []
created_date: '2026-10-19 05:51'
labels:
  - packaging
  - autostart
  - macos
dependencies:
  - TASK-112.01
  - TASK-112.02
references:
  - docs/reports/2026-10-19-background-server-research.md
parent_task_id: TASK-112
ordinal: 218000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The plist starts `/usr/bin/open -a <bundle>` (scribe/autostart.py:317), which returns at once, so launchd watches nothing and logs nothing. The research note gives the plist: ProgramArguments to Contents/MacOS/MyScribe, KeepAlive SuccessfulExit false, ProcessType Interactive, AssociatedBundleIdentifiers, StandardOutPath in ~/Library/Logs/MyScribe.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The plist written matches the one in the research note, and a test asserts its keys
- [ ] #2 An app running from an AppTranslocation path is not registered, and Settings says why
- [ ] #3 Switching on loads the agent now with launchctl bootstrap, switching off unloads it with bootout
- [ ] #4 The macOS walk (log out and in, /health, no window) is added to docs/macos-acceptance.md and reads not run until it is run
<!-- AC:END -->
