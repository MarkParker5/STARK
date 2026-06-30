from pathlib import Path

from stark.core.command import Response
from stark.general.localisation import LocalizableString, Localizer


def _create_strings_file(root: Path, lang: str, name: str, content: str):
    d = root / "strings" / lang
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.strings").write_text(content)


def test_localizable_string_basic():
    s = LocalizableString("greeting", "en", name="World")
    assert s.string == "greeting"
    assert s.language_code == "en"
    assert s.arguments == {"name": "World"}


def test_localizable_string_str():
    s = LocalizableString("greeting", "en")
    assert str(s) == "greeting"


def test_localizable_string_repr():
    s = LocalizableString("greeting", "en", name="World")
    r = repr(s)
    assert "LocalizableString" in r
    assert "greeting" in r
    assert "en" in r


def test_localizable_string_default_language():
    s = LocalizableString("greeting")
    assert s.language_code == "base"


def test_localize_plain_str():
    localizer = Localizer(languages=set())
    assert localizer.localize("plain string") == "plain string"


def test_localize_resolves_key(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "localizable", '"greeting" = "Hello, {name}!";')
    _create_strings_file(tmp_path, "ru", "localizable", '"greeting" = "Привет, {name}!";')
    _create_strings_file(tmp_path, "en", "recognizable", '"x" = "x";')
    _create_strings_file(tmp_path, "ru", "recognizable", '"x" = "x";')
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en", "ru"})
    localizer.load()

    en = LocalizableString("greeting", "en", name="Mark")
    assert localizer.localize(en) == "Hello, Mark!"

    ru = LocalizableString("greeting", "ru", name="Mark")
    assert localizer.localize(ru) == "Привет, Mark!"


def test_localize_falls_back_to_key(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "localizable", '"other" = "other";')
    _create_strings_file(tmp_path, "en", "recognizable", '"x" = "x";')
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    s = LocalizableString("missing_key", "en")
    assert localizer.localize(s) == "missing_key"


def test_localize_no_arguments(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "localizable", '"hello" = "Hello!";')
    _create_strings_file(tmp_path, "en", "recognizable", '"x" = "x";')
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    s = LocalizableString("hello", "en")
    assert localizer.localize(s) == "Hello!"


def test_response_accepts_localizable_string():
    r = Response(
        text=LocalizableString("greeting", "en", name="World"),
        voice=LocalizableString("greeting", "en", name="World"),
    )
    assert isinstance(r.text, LocalizableString)
    assert isinstance(r.voice, LocalizableString)
    assert r.text.string == "greeting"


def test_response_accepts_plain_str():
    r = Response("hello", voice="hello")
    assert r.text == "hello"
    assert r.voice == "hello"
