---
id: TASK-112.02
title: >-
  The launcher exits non-zero when the app dies, and zero on a clean stop or a
  configuration problem
status: Done
assignee:
  - '@claude'
created_date: '2026-10-19 05:51'
updated_date: '2026-10-20 20:27'
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
- [x] #1 A dead app child ends the launcher with its own documented non-zero code; a test kills the child and asserts it
- [x] #2 A clean stop, another instance already serving, and a configuration problem (no library drive, port busy, offline sync) end with 0, and each is written to launcher.log
- [x] #3 Errors printed before a Layout exists (main, :2947-2970) also reach a log file in a headless start
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. APP_DIED = 70 (sysexits EX_SOFTWARE) as the one non-zero code of the server doors; documented on the constant.
2. run_headless: the loop ending by itself reads the app's exit code. Non-zero: an error line in launcher.log naming app.log, return APP_DIED. Zero (an app that stopped itself, 112.03's stop route later): a line, return 0. Ctrl+C or SIGTERM: a line 'stopped', return 0.
3. first_run False (port busy, no room, failed sync, an app that never became ready) returns 0. Each already reports through Launch.report, so it is in launcher.log. Choice: an app that never answered at start counts as configuration, not as a crash, because restarting it repeats the same failure every ten seconds under launchd.
4. main: a missing home or adopted library ends 0 on the server doors (window and headless), 1 on the one-job doors (--sync-only, --doctor, --smoke), which CI and scripts read as pass/fail.
5. Errors before a Layout exists go to a log beside the pointer file (MyScribe-launcher.log next to MyScribe.location), timestamped; its folder always exists. Lines a fresh home could not hold (port busy before the home is made) go there too.
6. Tests first, red then green: a killed real child gives 70 with the line in launcher.log; a child that exits 0 gives 0; each configuration problem gives 0 with its line; the unplugged drive in a headless start lands in the early log. The three existing tests that asserted 1 for a server door move to 0, shown as a diff.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented (branch feat/task-112.02-launcher-exit-codes).
- APP_DIED = 70 (EX_SOFTWARE) documents the contract on the constant. run_headless reads AppProcess.exit_code() when the loop ends by itself: non-zero logs 'MyScribe stopped unexpectedly (exit code N); see .../app.log' and returns 70; zero logs 'MyScribe stopped.' and returns 0. Ctrl+C/SIGTERM logs 'MyScribe was stopped.' and returns 0.
- first_run False and a serving instance return 0; their sentence was already reported through Launch.report. Lines a fresh home could not hold (Launch.log.pending) go to the early log.
- main: missing home or adopted library returns 0 on the serving doors, 1 on --sync-only/--doctor/--smoke. Errors said before the Layout go to early_log_path() = MyScribe-launcher.log beside MyScribe.location, timestamped.
- Choice: an app that never answered at start counts as a configuration problem (0), not a crash, because a restart repeats it every ~10 s under launchd.
Evidence:
- Red (scratchpad red-112.02.txt): 7 failed, 2 passed (the two passing are guards: already-serving was already 0, --sync-only already 1).
- Green: test_launcher 128 passed 2 skipped; library 12; sitting 73; install 56; autostart 33; uninstall_text 5; build_release 6 (suite-112.02.txt).
- Three existing assertions moved 1 -> 0 (console disk refusal, at-login broken pointer, gone adopted library), each now also asserting the early log.
- Real process (real-112.02.txt): launcher script with LOCALAPPDATA pointing at a pointer to a missing folder: exit 0, the sentence timestamped in MyScribe-launcher.log, no default home made; --sync-only over it: exit 1.
Not verified: a crash of the real app under a real launcher (tests kill a real child process inside a real Launch, not python -m scribe); a supervisor reading the code is TASK-112.05/.06.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The headless launcher now ends with 70 (APP_DIED) only when the app child dies, and with 0 on a clean stop, another instance serving, or a configuration problem, each said in launcher.log. Errors said before a home exists go to MyScribe-launcher.log beside MyScribe.location. The one-job doors keep 1. Verified red then green (7 failed -> all pass; launcher family per file green), three old assertions moved 1 -> 0 with a diff, and a real launcher process over a missing home exited 0 with the timestamped line in the early log. Not verified: a crash of the real python -m scribe app; supervisors that read the code come in TASK-112.05/.06.
<!-- SECTION:FINAL_SUMMARY:END -->
