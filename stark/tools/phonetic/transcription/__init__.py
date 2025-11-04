from .protocol import IpaProvider
from .espeak import EspeakIpaProvider
from .ipa2lat import ipa2lat
from functools import lru_cache


@lru_cache
def transcription(
    string: str,
    language_code: str,
    ipa_provider: IpaProvider = EspeakIpaProvider(),
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
