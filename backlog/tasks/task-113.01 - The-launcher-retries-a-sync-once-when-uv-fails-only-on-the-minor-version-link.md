---
id: TASK-113.01
title: The launcher retries a sync once when uv fails only on the minor version link
status: To Do
assignee: []
created_date: '2026-10-19 18:15'
labels:
  - packaging
  - windows
  - bug
dependencies: []
references:
  - 'https://github.com/rvdbreemen/MyScribe/issues/16'
  - packaging/launcher/myscribe_launcher.py
parent_task_id: TASK-113
ordinal: 223000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the simulation of issue 16 the interpreter is complete after the failure, and a rerun of the same `uv sync` (with or without `--python <patch dir>\python.exe`) exits 0 and builds the env. The launcher can do that rerun itself instead of telling the user to start again. Whether this helps against a real os error 448 is not known until the reporter answers or it is reproduced.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 When `uv sync` exits non-zero and its output holds `Failed to create Python minor version link directory`, the launcher runs the sync once more, with `--python` pointing at the installed patch interpreter under the python dir, and says in the window that it does
- [ ] #2 Any other sync failure is not retried
- [ ] #3 A unit test with a fake uv shows red without the retry and green with it
- [ ] #4 The scratch simulation (a plain file planted at the minor link path, bundled uv, a one-line project) is re-run through the launcher sync and ends with a working env; command and output are in the task notes
- [ ] #5 The notes say plainly that a real os error 448 was not tested
<!-- AC:END -->
