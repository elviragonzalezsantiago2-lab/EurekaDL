from gui.eureka_gui import run_terminal_preflight


def test_preflight_requires_confirmation():
    messages = []

    approved = run_terminal_preflight(
        input_func=lambda _prompt: "n",
        output_func=messages.append,
        executable_lookup=lambda _name: "/tool/path",
    )

    assert not approved
    assert any("pre-download checklist" in message for message in messages)


def test_preflight_accepts_spanish_confirmation():
    assert run_terminal_preflight(
        input_func=lambda _prompt: "sí",
        output_func=lambda _message: None,
        executable_lookup=lambda _name: None,
    )
