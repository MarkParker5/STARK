from __future__ import annotations

from stark.general.localisation.localizer import Localizer
from stark.tools.dictionary.dictionary import Dictionary
from stark.tools.dictionary.models import DictionaryStorageProtocol
from stark.tools.dictionary.storage.storage_memory import DictionaryStorageMemory
from stark.tools.phonetic.transcription import EspeakIpaProvider, IpaProvider


def build_recognizable_dictionary(
    localizer: Localizer,
    ipa_provider: IpaProvider = EspeakIpaProvider(),
    storage: DictionaryStorageProtocol | None = None,
) -> Dictionary:
    """Build a Dictionary populated from all loaded recognizable.strings bundles.

    Each keyword from every language's recognizable.strings is added to the
    dictionary with its source language, enabling cross-language phonetic
    matching via the standard Dictionary lookup infrastructure.
    """
    dictionary = Dictionary(
        storage=storage or DictionaryStorageMemory(),
        ipa_provider=ipa_provider,
    )
    for lang, strings_file in localizer.recognizable.items():
        for entry in strings_file.strings.values():
            dictionary.write_one(lang, entry.value)
    return dictionary
