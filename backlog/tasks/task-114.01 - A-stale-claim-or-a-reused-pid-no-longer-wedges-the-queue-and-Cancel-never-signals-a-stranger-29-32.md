---
id: TASK-114.01
title: >-
  A stale claim or a reused pid no longer wedges the queue, and Cancel never
  signals a stranger (#29, #32)
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T19:49:00Z'
updated_date: '2026-10-21T19:49:00Z'
labels:
  - audit
dependencies: []
parent_task_id: TASK-114
ordinal: 228000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub #29: reconcile skipped a running row with pid NULL and started_at set for ever, so a crash between claim and spawn closed the queue permanently. #32: a live pid reused inside the 60 s slack kept the row running, and Cancel's kill_orphan signalled that stranger's process group.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A running row with no pid older than the slack is reconciled to interrupted and Cancel ends it; a fresh claim is still left alone
- [x] #2 A live pid that is not shaped like a runner (POSIX: not a session leader; Windows: not this app's python) neither keeps the row nor is signalled by kill_orphan
- [x] #3 Tests went red first and pass on Windows and POSIX
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
claim_is_fresh(row): pid NULL counts as a claim in flight only for _PID_AGE_SLACK_SECONDS. could_be_runner(pid): POSIX getsid(pid)==pid, Windows QueryFullProcessImageNameW basename == sys.executable's; only a clear no counts. runner_alive(row) = pid_alive and could_be_runner and not younger; reconcile and the cancel route both use it; kill_orphan refuses a non-runner.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evidence (scratchpad red-29-32.txt, green-29-32.txt, wsl-29-32.txt): red 5 supervisor + 1 app failed (on Windows kill_orphan did end the cmd.exe stranger). Green Windows: supervisor 31+1s, app 26, jobs 25, runner 14, web_jobs 44, web_settings 60. WSL: supervisor 32, app 26, web_jobs 44. Three tests modelled a live runner with a process that was no session leader; they now start it the way _spawn does. Two tests seeded a running pid-NULL row with started_at=1, which reconcile now rightly clears; they use a fresh claim.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
reconcile and Cancel clear a claim that never got a runner after the 60 s slack, and treat a live pid that is not shaped like a runner as gone, without signalling it. Red then green on Windows and in WSL.
<!-- SECTION:FINAL_SUMMARY:END -->
