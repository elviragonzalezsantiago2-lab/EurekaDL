from pathlib import Path

from orpheus import core


class _Session:
    settings = {"global": {"general": {"download_path": "downloads"}}}
    module_controls = {}


def test_core_download_uses_configured_path_when_output_is_omitted(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    captured = {}

    class DummyDownloader:
        def __init__(self, _settings, _controls, _printer, path):
            captured["path"] = path

    monkeypatch.setattr(core, "Downloader", DummyDownloader)

    core.orpheus_core_download(_Session(), {}, {}, "default", None)

    assert captured["path"] == str(tmp_path / "downloads")
    assert Path(captured["path"]).is_dir()
