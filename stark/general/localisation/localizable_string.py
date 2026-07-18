from stark.general.localisation.language_code import LanguageCode


class LocalizableString:
    """A deferred-localization string for response output.

    Stores a translation key + language code + format arguments. At response
    time, ``Localizer.localize()`` first resolves the translated template from
    ``localizable.strings``, then injects the arguments into it. This order
    matters — argument positions and surrounding text differ between languages,
    so formatting must happen after translation, not before.

    Example::

        # In a command runner:
        return Response(
            text=LocalizableString("greeting", "fr", name="Mark"),
            voice=LocalizableString("greeting", "fr", name="Mark"),
        )

        # strings/fr/localizable.strings: "greeting" = "Bonjour, {name}!";
        # Localizer resolves "greeting" for "fr" → "Bonjour, {name}!"
        # Then formats → "Bonjour, Mark!"
    """

    string: str
    language_code: LanguageCode
    arguments: dict[str, str]

    def __init__(self, string: str, language_code: LanguageCode = "base", /, **arguments: str):
        self.string = string
        self.language_code = language_code
        self.arguments = arguments

    def __str__(self) -> str:
        return self.string

    def __repr__(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in self.arguments.items())
        return f"LocalizableString({self.string!r}, {self.language_code!r}{', ' + args if args else ''})"
