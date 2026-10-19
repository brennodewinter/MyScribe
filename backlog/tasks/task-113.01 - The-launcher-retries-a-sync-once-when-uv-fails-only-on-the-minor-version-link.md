---
id: TASK-113.01
title: The launcher retries a sync once when uv fails only on the minor version link
status: Done
assignee:
  - '@claude'
created_date: '2026-10-19 18:15'
updated_date: '2026-10-19 20:38'
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
- [x] #1 When `uv sync` exits non-zero and its output holds `Failed to create Python minor version link directory`, the launcher runs the sync once more, with `--python` pointing at the installed patch interpreter under the python dir, and says in the window that it does
- [x] #2 Any other sync failure is not retried
- [x] #3 A unit test with a fake uv shows red without the retry and green with it
- [x] #4 The scratch simulation (a plain file planted at the minor link path, bundled uv, a one-line project) is re-run through the launcher sync and ends with a working env; command and output are in the task notes
- [x] #5 The notes say plainly that a real os error 448 was not tested
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Test first (tests/test_launcher.py): a fake uv that fails once with the minor-link line, then succeeds; assert sync() retries once with --python <installed patch interpreter>, says so, and stamps. Plus: another failure is not retried; the link line without an interpreter on disk is not retried; a retry that fails again fails once, not in a loop.
2. Show red.
3. Implement in sync(): record the lines, match the uv message, find the patch interpreter under layout.python_dir (highest cpython-X.Y.Z dir, no +variants), rerun sync_command + --python once.
4. Green; run test_launcher.py.
5. Re-run the scratch simulation through launcher.sync with the bundled uv 0.12.13; record command and output in the notes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in packaging/launcher/myscribe_launcher.py: `MINOR_LINK_FAILURE`, `downloaded_python(layout)` (newest `cpython-X.Y.Z-*` folder under the python dir with its interpreter; the `cpython-X.Y-*` link name and `+` variants are skipped), and a single retry in `sync()` with `--python <that interpreter>` when the first run failed and printed the link line.

Tests (tests/test_launcher.py), red before the change:
`.venv/Scripts/python -m pytest -q tests/test_launcher.py -k "minor_version_link or other_sync_failure or without_a_downloaded or retry_that_fails"` -> `2 failed, 2 passed` (the two retry tests failed; the two do-not-retry guards already held). After: `4 passed`.
- test_a_sync_that_fails_only_on_the_minor_version_link_is_retried_with_the_downloaded_python
- test_any_other_sync_failure_is_not_retried
- test_the_link_failure_is_not_retried_without_a_downloaded_python
- test_a_retry_that_fails_too_is_reported_once_and_not_repeated
Launcher files after the change: test_launcher.py 113 passed, 2 skipped; test_launcher_sitting.py 72 passed; test_launcher_library.py 12 passed; test_install.py 56 passed; test_uninstall_text.py 5 passed.

Simulation through `launcher.sync` (2026-10-19, Windows 11, the bundled uv 0.12.13; a one-line project with requires-python ==3.12.*, a plain file planted at `home/python/cpython-3.12-windows-x86_64-none`, everything in the scratchpad):
- launcher from origin/main: `error: Failed to create Python minor version link directory` / `uv sync failed with exit code 2` / `sync returned False | stamp: False | env python: False`.
- this branch: the same error, then `uv could not make its Python folder link; trying once more with the Python it already downloaded (cpython-3.12.14-windows-x86_64-none)`, `Using CPython 3.12.14 interpreter at: python\cpython-3.12.14-windows-x86_64-none\python.exe`, `Creating virtual environment at: env`, `sync returned True | stamp: True | env python: True`; the env python reports 3.12.14.

NOT tested: a real os error 448. The simulated failure reaches the same uv error branch with os error 267. Whether the retry beats 448 on the reporters machine is open until issue 16 answers. Also not checked by eye: the retry line in the Tk window; it goes through the same `report("busy", ...)` path as every uv line.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The launcher retries a uv sync once, with --python naming the interpreter uv already unpacked, when the first run failed on the Python minor version link (issue 16, ADR-027). Verified by four new tests in tests/test_launcher.py (2 red before, 4 green after; launcher files all green) and by the scratch simulation through launcher.sync with the bundled uv 0.12.13: main returns False, this branch builds a working 3.12.14 env. A real os error 448 is not tested.
<!-- SECTION:FINAL_SUMMARY:END -->
