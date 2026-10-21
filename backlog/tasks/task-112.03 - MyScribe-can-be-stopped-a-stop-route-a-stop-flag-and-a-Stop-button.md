---
id: TASK-112.03
title: 'MyScribe can be stopped: a stop route, a --stop flag and a Stop button'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-19 05:51'
updated_date: '2026-10-21 06:07'
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
- [x] #1 Robert has chosen what a stop does to a running job, and that choice is recorded
- [x] #2 A loopback-only POST stops the server cleanly, so supervisor, watcher and feeds end through the lifespan; a cross-site POST is refused by scribe.guard as today
- [x] #3 `MyScribe --stop` calls it and falls back to a hard stop after a timeout; a test covers both paths
- [x] #4 The web UI has a Stop MyScribe action that says what happens to a running job
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Robert chose (2026-10-21, AskUserQuestion): a stop puts the running job back at the front of the queue; the route is loopback + scribe.guard, no token file. Recorded as ADR-028 (Proposed).
2. Supervisor.stop(requeue=True): _watch ends the runner tree, waits, removes scratch, then jobs.requeue_running (front of its priority, started_at/pid/stage cleared; a cancel asked first wins). Join waits REQUEUE_STOP_SECONDS (20 s).
3. scribe/shutdown.stop_requested: loopback client, request_exit (uvicorn should_exit, wired in __main__), sets app.state.stop_requested so the lifespan stops the supervisor with requeue. POST /api/shutdown and POST /settings/stop share it. /health gains pid and launcher_pid.
4. Launcher --stop: read /health, POST the route, wait for the pid (not the port), STOP_WAIT 60 s; fallback end_tree on the launcher pid (POSIX SIGTERM, so the launcher exits 0 and no supervisor restarts it) or the app pid; pid_alive via OpenProcess on Windows, never os.kill(pid, 0). Lines also go to the early log.
5. Settings card Stop MyScribe in the Start at login section; window says STOPPED when the app exits 0.
6. Tests red then green on Windows and in WSL; a real app stopped by the real launcher; screenshots before and after.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence (scratchpad):
- Red: red-112.03-app.txt (supervisor 2 failed/1 guard passed; app 4 failed/2 guards passed), red-112.03-launcher.txt (5 failed), red-112.03-ui.txt (2 failed/1 guard passed).
- Green per file on Windows (suite-112.03.txt): supervisor 26+1s, jobs 25, app 25, web_settings 60, launcher 133+2s, library 12, sitting 73, runner 14, guard 11, autostart 33, install 56.
- WSL/POSIX under setsid (wsl-112.03.txt): supervisor 27, app 25, web_settings 55+5s, launcher 134+1s, library 12. The WSL venv lacked segno and had an old pyproject; installed segno 1.6.6 there, an environment fix, not a code change.
- Real run (e2e-112.03/stop.txt): python -m scribe on 4298 with a temp SCRIBE_DATA_DIR and two slow fake jobs; launcher --stop: exit 0, runner and app gone, /health silent, job 1 queued ahead of job 2 with pid/started_at/stage cleared; app log: app.stop_requested, job.requeued, runner.exited (info), app.stop; server exit 0.
- Screenshots (ui-112.03/stop-card-before.png, stop-card-after.png) via headless Chrome CDP: the card before, and 'MyScribe is stopping. Job 1 was running: it is back at the front of the queue...' after; the job stayed queued. The upper card shows the real Run value of this machine, so the images stay out of the PR.
- Pinned /health body test moved: two fields added (pid, launcher_pid).
Not verified: the hard-stop path against the real app (tested with a fake server that ignores the route and an orphaned process); the launcher_pid path under a real launcher; macOS. Open in ADR-028: whether window Quit, Ctrl+C and SIGTERM should also requeue.

Review follow-up:
- Hard stop in production names a launcher_pid. end_tree now gives a launcher LAUNCHER_STOP_WAIT (2 x STOP_TIMEOUT + 10 s) before SIGKILL, because its own AppProcess.stop may take two STOP_TIMEOUTs over a hung app; then ends the app itself if it outlived the launcher. New test test_the_hard_stop_ends_the_launcher_so_it_exits_clean_and_takes_its_app (orphaned fake launcher + app): Windows 6 passed (stop tests), WSL test_launcher 135 passed 1 skipped. Not red first: the old code passes it too with a fast fake launcher; the >15 s timing is not under test.
- Measured in WSL (scratchpad wsl-quit-runner.txt): SIGTERM to the app's group leaves the runner (own session) running; it wrote done 13 s later. ADR-028's context corrected: interrupted on Windows, an orphaned runner on POSIX.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
MyScribe can be stopped: POST /api/shutdown (loopback, scribe.guard), MyScribe --stop with a hard fallback after 60 s, and a Stop MyScribe card in Settings. Per ADR-028 (Robert's choice, Proposed) a stop ends the runner, then puts its job back at the front of the queue; a hard stop leaves it interrupted and says so. Verified red then green on Windows and POSIX (WSL), a real app stopped by the real launcher with the job requeued, and before/after screenshots.
<!-- SECTION:FINAL_SUMMARY:END -->
