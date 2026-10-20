---
id: TASK-113.02
title: >-
  A failed install says what failed: no internet advice for a non-network error,
  and the Setup button does not pretend MyScribe starts
status: Done
assignee:
  - '@claude'
created_date: '2026-10-19 18:15'
updated_date: '2026-10-20 01:53'
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
- [x] #1 The internet advice appears only when the uv output points at the network (download, DNS, TLS, proxy); otherwise the line says the install failed on this computer and points at the log
- [x] #2 The Setup button with no env python says the speech engine is not installed yet and offers no sitting; it never says MyScribe starts anyway
- [x] #3 Tests cover both messages, red before and green after
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Prepare collects the sync lines it reports and asks install_failure for the closing sentence: internet advice only when a uv network marker is in the lines, otherwise "failed on this computer" plus the launcher.log path.
2. Markers taken from real uv 0.12.13 output (closed proxy, unknown Python host, unknown index host), not from memory; "proxy" left out because proxy_note adds it to every failed sync on a proxy machine.
3. setup_plan: when the plan child cannot start and the env python does not exist, say the speech engine is not installed yet; no sitting, no "starts anyway".
4. Tests red first, then green; a real Launch.prepare run with the bundled uv for both sentences, main vs branch.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence (2026-10-20):
- Red before the fix: 2 failed, 1 passed (the network test already held; the Setup test failed with the exact issue-16 text "The setup questions could not be read: [WinError 2] The system cannot find the file specified. MyScribe starts anyway; ..."). Green after: 3 passed. Plus 3 parametrized cases for the captured uv outputs and 1 for a configured proxy alone.
- Files: test_launcher.py 119 passed, 2 skipped; test_launcher_sitting.py 73; test_launcher_library.py 12; test_install.py 56; test_uninstall_text.py 5.
- Real run, Launch.prepare with the bundled uv 0.12.13 (scratchpad run_launcher_prepare.py, output prepare-113.02.txt): closed proxy -> internet sentence on main and branch; a file where the env folder goes -> main says "Check the internet connection", branch says "Installing failed on this computer ... launcher.log", and that log holds the uv error line.
- Not verified: the Setup button pressed in the real Tk window; the sentence was checked through open_sitting, the function the button calls.
- Open-source check: not applicable, a few lines of project-specific message logic.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
A failed sync now gives internet advice only when uv printed a network marker (captured from real uv 0.12.13 output); otherwise it says the install failed on this computer and names launcher.log. The Setup button before the engine exists says it is not installed yet, without WinError 2 or "starts anyway". Verified red-then-green in test_launcher.py and test_launcher_sitting.py and by a real Launch.prepare run with the bundled uv, main vs branch.
<!-- SECTION:FINAL_SUMMARY:END -->
