from functools import lru_cache

from stark.general.localisation.language_code import LanguageCode

from .espeak import EspeakIpaProvider
from .ipa2lat import ipa2lat
from .latin_passthrough import LatinPassthroughProvider
from .protocol import IpaProvider

# Module-level default so it is not constructed as a call in argument defaults (B008).
_DEFAULT_IPA_PROVIDER = EspeakIpaProvider()


@lru_cache
def transcription(
    string: str,
    language_code: LanguageCode,
    ipa_provider: IpaProvider = _DEFAULT_IPA_PROVIDER,
) -> str:
    """
    Converts a string to a simplified latin transcription via phonetic (IPA) transliteration.

    Args:
        string: The input string to transcribe.
        language_code: The language code for IPA conversion.
        ipa_provider: The IPA provider to use for conversion (default: EspeakIpaProvider).

    Returns:
        The simplified latin transcription of the input string.
    """
    return " ".join(
        ipa2lat(ipa_provider.to_ipa(word, language_code)) for word in string.split()
    )
