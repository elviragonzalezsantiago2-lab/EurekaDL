from pathlib import Path

import eureka


def test_doctor_reports_installation_state(monkeypatch, tmp_path, capsys):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "settings.json").write_text("{}", encoding="utf-8")
    module = tmp_path / "modules" / "demo"
    module.mkdir(parents=True)
    (module / "interface.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(eureka.shutil, "which", lambda name: "/usr/bin/ffmpeg" if name == "ffmpeg" else None)

    eureka.run_doctor(tmp_path)

    output = capsys.readouterr().out
    assert "FFmpeg: found" in output
    assert "Configuration: found" in output
    assert "Modules: 1 (demo)" in output


def test_doctor_handles_a_fresh_project(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(eureka.shutil, "which", lambda _name: None)

    eureka.run_doctor(Path(tmp_path))

    output = capsys.readouterr().out
    assert "FFmpeg: missing" in output
    assert "Configuration: not created yet" in output
    assert "Modules: 0" in output
