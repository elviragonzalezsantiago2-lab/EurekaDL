import eureka
from gui.eureka_gui import build_login_command


def test_tidal_login_command_uses_tv_mode():
    assert build_login_command("tidal")[-2:] == ["--mode", "tv"]


def test_browser_platform_login_reports_setup_guidance(capsys):
    assert eureka.run_platform_login("spotify") == 0
    assert "SPOTIPY_CLIENT_ID" in capsys.readouterr().out
