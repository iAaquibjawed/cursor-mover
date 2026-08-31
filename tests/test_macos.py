"""Tests for AppleScript generation. These do not invoke osascript."""

from __future__ import annotations

from cursor_mover import macos


class TestApplescriptQuote:
    def test_wraps_plain_text(self) -> None:
        assert macos.applescript_quote("hello") == '"hello"'

    def test_escapes_double_quotes(self) -> None:
        assert macos.applescript_quote('say "hi"') == '"say \\"hi\\""'

    def test_escapes_backslashes_before_quotes(self) -> None:
        assert macos.applescript_quote("a\\b") == '"a\\\\b"'

    def test_neutralises_script_injection(self) -> None:
        quoted = macos.applescript_quote('" & (do shell script "whoami") & "')
        assert quoted.startswith('"') and quoted.endswith('"')
        # Every inner quote is escaped, so the literal never terminates early.
        assert quoted.count('"') - quoted.count('\\"') == 2


class TestPromptForText:
    def test_cancel_exit_code_is_not_confirmed(self, monkeypatch) -> None:
        monkeypatch.setattr(macos, "_run_osascript", lambda script, timeout: _Result(1, ""))
        assert macos.prompt_for_text("t", "m", "11").confirmed is False

    def test_missing_osascript_is_not_confirmed(self, monkeypatch) -> None:
        monkeypatch.setattr(macos, "_run_osascript", lambda script, timeout: None)
        assert macos.prompt_for_text("t", "m", "11").confirmed is False

    def test_parses_button_and_text(self, monkeypatch) -> None:
        payload = f"Set{macos._FIELD_SEPARATOR}42"
        monkeypatch.setattr(macos, "_run_osascript", lambda script, timeout: _Result(0, payload))
        response = macos.prompt_for_text("t", "m", "11")
        assert response.confirmed is True
        assert response.text == "42"

    def test_text_containing_the_default_separator_char_is_safe(self, monkeypatch) -> None:
        payload = f"Cancel{macos._FIELD_SEPARATOR}whatever"
        monkeypatch.setattr(macos, "_run_osascript", lambda script, timeout: _Result(0, payload))
        assert macos.prompt_for_text("t", "m", "11").confirmed is False


class _Result:
    def __init__(self, returncode: int, stdout: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ""
