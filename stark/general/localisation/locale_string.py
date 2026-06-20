from __future__ import annotations

from stark.general.localisation.language_code import LanguageCode


class LocaleString(str):
    """A str subclass that carries language metadata.

    Behaves exactly like a regular string — equality, hashing, ``in``, regex,
    len, iteration, and all comparison operators work unchanged because
    ``LocaleString`` inherits from ``str`` and does not override those.

    Metadata propagation
    --------------------
    All str methods that return a *new* string (``replace``, ``strip``,
    slicing, ``split``, ``join``, ``format``, ``upper``, ``lower``, etc.)
    are overridden to return ``LocaleString`` instances that keep the
    original ``language_code``.

    Known limitation: CPython's C-level functions (notably ``re.sub``)
    construct plain ``str`` internally and bypass Python-level overrides,
    so their return values lose metadata.

    If a future method override cannot preserve metadata, it should emit a warning:

        ``"<method> strips LocaleString metadata; use explicit str() to
        silence this warning"``

    Use ``str(locale_string)`` to intentionally downcast to a plain
    ``str`` when metadata is not needed or when calling APIs that would
    otherwise trigger the warning.

    Extensibility
    -------------
    Designed as the base carrier for locale context through the parsing
    pipeline. Future subclasses (e.g. ``TranscriptionString``) can attach
    richer STT metadata (word-level timestamps, confidence, per-word
    language tags) without changing method signatures — ``did_parse``
    always receives a ``LocaleString`` (or subclass), and code that
    only needs the text keeps working as before.
    """

    language_code: LanguageCode

    def __new__(cls, value: str = "", language_code: LanguageCode = "base") -> LocaleString:
        instance = super().__new__(cls, value)
        instance.language_code = language_code
        return instance

    def _with(self, value: str) -> LocaleString:
        return LocaleString(value, self.language_code)

    # --- operators ---

    def __getitem__(self, key) -> LocaleString:
        return self._with(super().__getitem__(key))

    def __add__(self, other: str) -> LocaleString:
        return self._with(super().__add__(other))

    def __radd__(self, other: str) -> LocaleString:
        return self._with(other.__add__(self))

    def __mul__(self, n: int) -> LocaleString:
        return self._with(super().__mul__(n))

    def __rmul__(self, n: int) -> LocaleString:
        return self._with(super().__rmul__(n))

    def __mod__(self, args) -> LocaleString:
        return self._with(super().__mod__(args))

    # --- str → str methods ---

    def replace(self, old: str, new: str, count: int = -1) -> LocaleString:
        return self._with(super().replace(old, new, count))

    def strip(self, chars: str | None = None) -> LocaleString:
        return self._with(super().strip(chars))

    def lstrip(self, chars: str | None = None) -> LocaleString:
        return self._with(super().lstrip(chars))

    def rstrip(self, chars: str | None = None) -> LocaleString:
        return self._with(super().rstrip(chars))

    def lower(self) -> LocaleString:
        return self._with(super().lower())

    def upper(self) -> LocaleString:
        return self._with(super().upper())

    def title(self) -> LocaleString:
        return self._with(super().title())

    def capitalize(self) -> LocaleString:
        return self._with(super().capitalize())

    def casefold(self) -> LocaleString:
        return self._with(super().casefold())

    def swapcase(self) -> LocaleString:
        return self._with(super().swapcase())

    def center(self, width: int, fillchar: str = " ") -> LocaleString:
        return self._with(super().center(width, fillchar))

    def ljust(self, width: int, fillchar: str = " ") -> LocaleString:
        return self._with(super().ljust(width, fillchar))

    def rjust(self, width: int, fillchar: str = " ") -> LocaleString:
        return self._with(super().rjust(width, fillchar))

    def zfill(self, width: int) -> LocaleString:
        return self._with(super().zfill(width))

    def expandtabs(self, tabsize: int = 8) -> LocaleString:
        return self._with(super().expandtabs(tabsize))

    def join(self, iterable) -> LocaleString:
        return self._with(super().join(iterable))

    def format(self, *args, **kwargs) -> LocaleString:
        return self._with(super().format(*args, **kwargs))

    def format_map(self, mapping) -> LocaleString:
        return self._with(super().format_map(mapping))

    def removeprefix(self, prefix: str) -> LocaleString:
        return self._with(super().removeprefix(prefix))

    def removesuffix(self, suffix: str) -> LocaleString:
        return self._with(super().removesuffix(suffix))

    # --- str → list[str] methods ---

    def split(self, sep: str | None = None, maxsplit: int = -1) -> list[LocaleString]:
        return [self._with(s) for s in super().split(sep, maxsplit)]

    def rsplit(self, sep: str | None = None, maxsplit: int = -1) -> list[LocaleString]:
        return [self._with(s) for s in super().rsplit(sep, maxsplit)]

    def splitlines(self, keepends: bool = False) -> list[LocaleString]:
        return [self._with(s) for s in super().splitlines(keepends)]

    # --- str → tuple[str, ...] methods ---

    def partition(self, sep: str) -> tuple[LocaleString, LocaleString, LocaleString]:
        a, b, c = super().partition(sep)
        return self._with(a), self._with(b), self._with(c)

    def rpartition(self, sep: str) -> tuple[LocaleString, LocaleString, LocaleString]:
        a, b, c = super().rpartition(sep)
        return self._with(a), self._with(b), self._with(c)

    # --- repr ---

    def __repr__(self) -> str:
        return f"LocaleString({super().__repr__()}, language_code={self.language_code!r})"
