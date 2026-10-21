"""MyScribe is EUPL-1.2, and every place that says so says the same.

The licence text, the package metadata, the README and the release payload are
four files; a licence that one of them forgets is a release that ships without
it.
"""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPDX = "EUPL-1.2"


def test_the_licence_text_is_the_eupl_1_2():
    text = (REPO / "LICENSE.md").read_text(encoding="utf-8")
    assert text.startswith("EUROPEAN UNION PUBLIC LICENCE v. 1.2")
    assert "Appendix" in text and "Compatible Licences" in text


def test_the_package_metadata_names_the_licence_and_its_file():
    project = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["license"] == SPDX
    assert project["license-files"] == ["LICENSE.md"]


def test_the_readme_says_who_holds_the_copyright_and_under_what_licence():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "Copyright © 2026 Robert van den Breemen." in readme
    assert "initiated and conceived by Robert van den Breemen" in readme
    assert f"SPDX-License-Identifier: {SPDX}" in readme
    assert "](LICENSE.md)" in readme


def test_a_release_ships_the_licence():
    spec = importlib.util.spec_from_file_location("build_payload", REPO / "packaging" / "build_payload.py")
    build_payload = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_payload)
    assert "LICENSE.md" in build_payload.APP_PATHS
    assert "MyScribe-LICENSE-EUPL-1.2.md" in (REPO / "packaging" / "build_payload.py").read_text(encoding="utf-8")
