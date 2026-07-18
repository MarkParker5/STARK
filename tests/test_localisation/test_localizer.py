import tempfile
from pathlib import Path

from stark.general.localisation import Localizer


def _create_strings_file(root: Path, lang: str, name: str, content: str):
    d = root / "strings" / lang
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.strings").write_text(content)


def test_localizer_loads_only_enabled_languages(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "recognizable", '"greeting" = "hello|hi";')
    _create_strings_file(tmp_path, "ru", "recognizable", '"greeting" = "привет|здравствуй";')
    _create_strings_file(tmp_path, "de", "recognizable", '"greeting" = "hallo|guten tag";')
    _create_strings_file(tmp_path, "en", "localizable", '"greeting" = "Hello!";')
    _create_strings_file(tmp_path, "ru", "localizable", '"greeting" = "Привет!";')
    _create_strings_file(tmp_path, "de", "localizable", '"greeting" = "Hallo!";')

    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en", "ru"})
    localizer.load()

    assert "en" in localizer.recognizable
    assert "ru" in localizer.recognizable
    assert "de" not in localizer.recognizable

    assert localizer.get_recognizable("greeting", "en") == "hello|hi"
    assert localizer.get_recognizable("greeting", "ru") == "привет|здравствуй"
    # "de" not loaded — falls back to base_language ("en")
    assert localizer.get_recognizable("greeting", "de") == "hello|hi"


def test_localizer_base_fallback(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "base", "recognizable", '"fallback_key" = "base_value";')
    _create_strings_file(tmp_path, "en", "recognizable", '"other_key" = "en_value";')
    _create_strings_file(tmp_path, "base", "localizable", '"fallback_key" = "base_value";')
    _create_strings_file(tmp_path, "en", "localizable", '"other_key" = "en_value";')

    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    assert localizer.get_recognizable("fallback_key", "en") == "base_value"
    assert localizer.get_recognizable("other_key", "en") == "en_value"


def test_localizer_get_localizable(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "localizable", '"hello" = "Hello!";')
    _create_strings_file(tmp_path, "en", "recognizable", '"hello" = "hello|hi";')

    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    assert localizer.get_localizable("hello", "en") == "Hello!"
    assert localizer.get_recognizable("hello", "en") == "hello|hi"
