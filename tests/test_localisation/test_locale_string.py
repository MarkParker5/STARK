import re

from stark.general.localisation.locale_string import LocaleString


def test_basic_creation():
    s = LocaleString("hello", "en")
    assert s == "hello"
    assert s.language_code == "en"
    assert isinstance(s, str)


def test_default_language():
    s = LocaleString("hello")
    assert s.language_code == "base"


def test_empty():
    s = LocaleString()
    assert s == ""
    assert s.language_code == "base"


def test_str_equality():
    s = LocaleString("hello", "ru")
    assert s == "hello"
    assert "hello" == s
    assert s in "say hello world"
    assert "ell" in s


def test_len():
    s = LocaleString("hello", "en")
    assert len(s) == 5


def test_hash_matches_str():
    s = LocaleString("hello", "en")
    assert hash(s) == hash("hello")
    assert {s} == {"hello"}


def test_bool():
    assert bool(LocaleString("hello", "en"))
    assert not bool(LocaleString("", "en"))


# --- Slicing ---

def test_getitem_single():
    s = LocaleString("hello", "ru")
    c = s[1]
    assert c == "e"
    assert isinstance(c, LocaleString)
    assert c.language_code == "ru"


def test_getitem_slice():
    s = LocaleString("hello world", "de")
    sliced = s[6:]
    assert sliced == "world"
    assert isinstance(sliced, LocaleString)
    assert sliced.language_code == "de"


def test_getitem_full_copy():
    s = LocaleString("hello", "fr")
    copy = s[:]
    assert copy == "hello"
    assert isinstance(copy, LocaleString)
    assert copy.language_code == "fr"


def test_getitem_range():
    s = LocaleString("hello world", "en")
    sub = s[0:5]
    assert sub == "hello"
    assert isinstance(sub, LocaleString)
    assert sub.language_code == "en"


# --- String methods returning str ---

def test_replace():
    s = LocaleString("foo bar baz", "ru")
    r = s.replace("bar", "")
    assert r == "foo  baz"
    assert isinstance(r, LocaleString)
    assert r.language_code == "ru"


def test_strip():
    s = LocaleString("  hello  ", "en")
    assert s.strip() == "hello"
    assert isinstance(s.strip(), LocaleString)
    assert s.strip().language_code == "en"


def test_lstrip_rstrip():
    s = LocaleString("  hello  ", "ja")
    assert s.lstrip().language_code == "ja"
    assert s.rstrip().language_code == "ja"


def test_lower_upper():
    s = LocaleString("Hello", "en")
    assert s.lower() == "hello"
    assert s.lower().language_code == "en"
    assert s.upper() == "HELLO"
    assert s.upper().language_code == "en"


def test_title_capitalize():
    s = LocaleString("hello world", "en")
    assert s.title() == "Hello World"
    assert s.title().language_code == "en"
    assert s.capitalize() == "Hello world"
    assert s.capitalize().language_code == "en"


def test_center_ljust_rjust():
    s = LocaleString("hi", "en")
    assert s.center(6).language_code == "en"
    assert s.ljust(6).language_code == "en"
    assert s.rjust(6).language_code == "en"


def test_zfill():
    s = LocaleString("42", "en")
    assert s.zfill(5) == "00042"
    assert s.zfill(5).language_code == "en"


def test_removeprefix_removesuffix():
    s = LocaleString("hello world", "en")
    assert s.removeprefix("hello ") == "world"
    assert s.removeprefix("hello ").language_code == "en"
    assert s.removesuffix(" world") == "hello"
    assert s.removesuffix(" world").language_code == "en"


# --- Concatenation ---

def test_add():
    s = LocaleString("hello", "ru")
    result = s + " world"
    assert result == "hello world"
    assert isinstance(result, LocaleString)
    assert result.language_code == "ru"


def test_radd():
    s = LocaleString("world", "ru")
    result = "hello " + s
    assert result == "hello world"
    assert isinstance(result, LocaleString)
    assert result.language_code == "ru"


def test_mul():
    s = LocaleString("ab", "en")
    assert (s * 3) == "ababab"
    assert (s * 3).language_code == "en"
    assert (3 * s) == "ababab"
    assert (3 * s).language_code == "en"


# --- Split / Join ---

def test_split():
    s = LocaleString("one two three", "de")
    parts = s.split()
    assert parts == ["one", "two", "three"]
    assert all(isinstance(p, LocaleString) for p in parts)
    assert all(p.language_code == "de" for p in parts)


def test_split_sep():
    s = LocaleString("a,b,c", "en")
    parts = s.split(",")
    assert parts == ["a", "b", "c"]
    assert all(p.language_code == "en" for p in parts)


def test_rsplit():
    s = LocaleString("a b c", "en")
    parts = s.rsplit(maxsplit=1)
    assert parts == ["a b", "c"]
    assert all(p.language_code == "en" for p in parts)


def test_splitlines():
    s = LocaleString("a\nb\nc", "en")
    lines = s.splitlines()
    assert lines == ["a", "b", "c"]
    assert all(l.language_code == "en" for l in lines)


def test_join():
    s = LocaleString(" ", "ru")
    result = s.join(["one", "two", "three"])
    assert result == "one two three"
    assert isinstance(result, LocaleString)
    assert result.language_code == "ru"


# --- Partition ---

def test_partition():
    s = LocaleString("hello world foo", "en")
    a, b, c = s.partition(" ")
    assert a == "hello"
    assert b == " "
    assert c == "world foo"
    assert all(isinstance(x, LocaleString) for x in (a, b, c))
    assert all(x.language_code == "en" for x in (a, b, c))


def test_rpartition():
    s = LocaleString("hello world foo", "en")
    a, b, c = s.rpartition(" ")
    assert a == "hello world"
    assert c == "foo"
    assert all(x.language_code == "en" for x in (a, b, c))


# --- Format ---

def test_format():
    s = LocaleString("hello {name}", "ru")
    result = s.format(name="world")
    assert result == "hello world"
    assert isinstance(result, LocaleString)
    assert result.language_code == "ru"


def test_format_map():
    s = LocaleString("{a} + {b}", "en")
    result = s.format_map({"a": "1", "b": "2"})
    assert result == "1 + 2"
    assert result.language_code == "en"


def test_mod_format():
    s = LocaleString("hello %s", "en")
    result = s % "world"
    assert result == "hello world"
    assert isinstance(result, LocaleString)
    assert result.language_code == "en"


# --- Regex compatibility ---

def test_regex_finditer():
    s = LocaleString("foo 123 bar 456", "en")
    matches = list(re.finditer(r"\d+", s))
    assert len(matches) == 2
    assert matches[0].group() == "123"
    assert matches[1].group() == "456"


def test_regex_sub():
    s = LocaleString("foo bar baz", "en")
    result = re.sub(r"bar", "qux", s)
    assert result == "foo qux baz"
    # re.sub returns plain str — this is expected
    assert type(result) is str


def test_regex_match():
    s = LocaleString("hello world", "ru")
    m = re.match(r"hello (\w+)", s)
    assert m is not None
    assert m.group(1) == "world"


# --- Interop ---

def test_str_methods_dont_crash():
    s = LocaleString("Hello World", "en")
    assert s.casefold().language_code == "en"
    assert s.swapcase().language_code == "en"
    assert s.expandtabs().language_code == "en"


def test_plain_str_passthrough():
    plain = "hello"
    locale = LocaleString(plain, "en")
    assert locale == plain
    assert plain == locale
    assert type(plain) is str
    assert isinstance(locale, str)


def test_repr():
    s = LocaleString("hello", "en")
    r = repr(s)
    assert "LocaleString" in r
    assert "en" in r
    assert "hello" in r


def test_str_downcast():
    s = LocaleString("hello", "ru")
    plain = str(s)
    assert plain == "hello"
    assert type(plain) is str
    assert not hasattr(plain, "language_code") or not isinstance(plain, LocaleString)


def test_re_sub_returns_plain_str():
    s = LocaleString("foo bar baz", "en")
    result = re.sub(r"bar", "qux", s)
    assert result == "foo qux baz"
    assert type(result) is str
