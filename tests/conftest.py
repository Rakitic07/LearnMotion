import pytest


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("LEARNMOTION_DB", str(tmp_path / "test.db"))
