import os
import stat

import pytest

from scribe import paths


def test_dirs_are_under_repo_data(tmp_path, monkeypatch):
    monkeypatch.setenv("SCRIBE_DATA_DIR", str(tmp_path / "d"))
    import importlib; importlib.reload(paths)
    paths.ensure_dirs()
    assert paths.DB_PATH.parent == paths.DATA_DIR
    assert paths.MEDIA_DIR.is_dir() and paths.LOGS_DIR.is_dir()
    assert paths.WORK_DIR.is_dir()


@pytest.mark.skipif(os.name == "nt", reason="mode bits are a POSIX answer; Windows has ACLs")
def test_a_data_dir_the_app_makes_is_private(tmp_path, monkeypatch):
    """The library holds transcripts, recordings and API keys: a fresh one
    starts at 0700, not the umask's 0755."""
    data = tmp_path / "fresh"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "MEDIA_DIR", data / "media")
    monkeypatch.setattr(paths, "LOGS_DIR", data / "logs")
    monkeypatch.setattr(paths, "WORK_DIR", data / "work")
    monkeypatch.setattr(paths, "MODELS_DIR", data / "models")

    paths.ensure_dirs()

    assert stat.S_IMODE(data.stat().st_mode) == 0o700


@pytest.mark.skipif(os.name == "nt", reason="mode bits are a POSIX answer; Windows has ACLs")
def test_a_data_dir_the_app_did_not_make_keeps_its_mode(tmp_path, monkeypatch):
    """A mode somebody chose on purpose is theirs: ensure_dirs must not
    tighten it back at every start."""
    data = tmp_path / "existing"
    data.mkdir(mode=0o755)
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "MEDIA_DIR", data / "media")
    monkeypatch.setattr(paths, "LOGS_DIR", data / "logs")
    monkeypatch.setattr(paths, "WORK_DIR", data / "work")
    monkeypatch.setattr(paths, "MODELS_DIR", data / "models")

    paths.ensure_dirs()

    assert stat.S_IMODE(data.stat().st_mode) == 0o755


def test_each_job_gets_its_own_work_directory():
    # Scratch space per job, so one job's leftovers can never be handed to
    # another and finalize can delete a whole directory without thinking.
    assert paths.job_work_dir(42).parent == paths.WORK_DIR
    assert paths.job_work_dir(42) != paths.job_work_dir(43)


# --- the database's name ---------------------------------------------------------------


def test_the_database_carries_the_applications_name(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
    monkeypatch.setattr(paths, "DB_PATH", tmp_path / "myscribe.db")

    assert paths.DB_PATH.name == "myscribe.db"
    assert paths.LEGACY_DB_NAME == "scribe.db"


def test_a_database_from_before_the_rename_is_adopted_with_its_sidecars(tmp_path, monkeypatch):
    """The three files move together: a .db without its -wal is a database
    missing its last transactions."""
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
    monkeypatch.setattr(paths, "DB_PATH", tmp_path / "myscribe.db")
    for name, body in (("scribe.db", b"db"), ("scribe.db-wal", b"wal"), ("scribe.db-shm", b"shm"),
                       ("scribe.db.backup-20260903", b"old")):
        (tmp_path / name).write_bytes(body)

    assert paths.adopt_legacy_db() is True

    assert (tmp_path / "myscribe.db").read_bytes() == b"db"
    assert (tmp_path / "myscribe.db-wal").read_bytes() == b"wal"
    assert (tmp_path / "myscribe.db-shm").read_bytes() == b"shm"
    assert not (tmp_path / "scribe.db").exists() and not (tmp_path / "scribe.db-wal").exists()
    assert (tmp_path / "scribe.db.backup-20260903").exists(), "backups are left alone"
    # Idempotent: nothing left to adopt.
    assert paths.adopt_legacy_db() is False


def test_adoption_never_overwrites_a_database_that_already_has_the_new_name(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
    monkeypatch.setattr(paths, "DB_PATH", tmp_path / "myscribe.db")
    (tmp_path / "myscribe.db").write_bytes(b"current")
    (tmp_path / "scribe.db").write_bytes(b"stale")

    assert paths.adopt_legacy_db() is False

    assert (tmp_path / "myscribe.db").read_bytes() == b"current"
    assert (tmp_path / "scribe.db").exists()


def test_connect_adopts_before_opening_the_default_database(tmp_path, monkeypatch):
    from scribe import db

    monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
    monkeypatch.setattr(paths, "DB_PATH", tmp_path / "myscribe.db")
    seed = db.connect(tmp_path / "scribe.db")
    db.migrate(seed)
    seed.execute("INSERT INTO setting(key, value) VALUES ('default_language', 'nl')")
    seed.commit()
    seed.close()

    conn = db.connect()  # no path: the default, adopted first
    try:
        row = conn.execute("SELECT value FROM setting WHERE key='default_language'").fetchone()
        assert row["value"] == "nl"
    finally:
        conn.close()
    assert (tmp_path / "myscribe.db").exists() and not (tmp_path / "scribe.db").exists()
