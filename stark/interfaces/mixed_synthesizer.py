from stark.general.localisation import LanguageCode
from stark.interfaces.protocols import SpeechSynthesizer, SpeechSynthesizerResult


class MixedSpeechSynthesizer(SpeechSynthesizer):
    """Routes each segment to the matching per-language SpeechSynthesizer.

    Falls back to the "base" engine, then to the first registered engine.
    """

    def __init__(self, synthesizers: dict[LanguageCode, SpeechSynthesizer]):
        assert synthesizers, "synthesizers dict must not be empty"
        assert all(isinstance(v, SpeechSynthesizer) for v in synthesizers.values())
        self._synthesizers = synthesizers

    async def synthesize_segment(self, text: str, language_code: LanguageCode) -> SpeechSynthesizerResult:
        engine = (
            self._synthesizers.get(language_code)
            or self._synthesizers.get("base")
            or next(iter(self._synthesizers.values()))
        )
        return await engine.synthesize_segment(text, language_code)
