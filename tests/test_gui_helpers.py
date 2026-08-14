from gui.eureka_gui import build_download_command, is_supported_url


def test_url_validation_requires_http_url():
    assert is_supported_url("https://example.com/track/123")
    assert is_supported_url("http://example.com")
    assert not is_supported_url("example.com/track/123")
    assert not is_supported_url("ftp://example.com/file")


def test_download_command_includes_optional_output_path():
    command = build_download_command("https://example.com/track", "/tmp/music")

    assert command[-2:] == ["--output", "/tmp/music"]
    assert command[-3] == "https://example.com/track"
