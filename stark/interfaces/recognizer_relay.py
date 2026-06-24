from __future__ import annotations

import logging
import time
from typing import Generator

import anyio
from asyncer._main import TaskGroup

from stark.general.localisation import LocaleString
from stark.interfaces.protocols import SpeechRecognizer, SpeechRecognizerDelegate
from stark.models.voice_transcription import (
    Transcription,
    VoiceTranscriptionTrack,
    VoiceTranscriptionWord,
)

logger = logging.getLogger(__name__)


class SpeechRecognizerRelay:
    """Broadcasts audio to N per-language recognizers, assembles the best transcription by confidence."""

    _speech_recognizers: list[SpeechRecognizer]
    _current_transcription: Transcription | None = None
    _delegate: SpeechRecognizerDelegate | None = None
    _is_recognizing: bool = False
    _convergence_timeout: float

    def __init__(
        self,
        speech_recognizers: list[SpeechRecognizer],
        convergence_timeout: float = 2.0,
    ):
        for recognizer in speech_recognizers:
            assert isinstance(recognizer, SpeechRecognizer)
        self._speech_recognizers = speech_recognizers
        self._convergence_timeout = convergence_timeout

    # --- properties ---

    @property
    def is_recognizing(self) -> bool:
        return self._is_recognizing

    @is_recognizing.setter
    def is_recognizing(self, value: bool):
        self._is_recognizing = value
        for recognizer in self._speech_recognizers:
            recognizer.is_recognizing = value

    @property
    def delegate(self) -> SpeechRecognizerDelegate | None:
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: SpeechRecognizerDelegate | None):
        self._delegate = delegate

    # --- public ---

    def start_speech_recognizers(self, task_group: TaskGroup):
        self.is_recognizing = True
        for recognizer in self._speech_recognizers:
            recognizer.delegate = self
            task_group.soonify(recognizer.start_listening)()

    async def start_listening(self):
        raise NotImplementedError("Use start_speech_recognizers() instead")

    def stop_listening(self):
        for recognizer in self._speech_recognizers:
            recognizer.stop_listening()

    def microphone_did_receive_sample(self, data):
        if not self.is_recognizing:
            return
        for recognizer in self._speech_recognizers:
            if hasattr(recognizer, "microphone_did_receive_sample"):
                recognizer.microphone_did_receive_sample(data)
            elif hasattr(recognizer, "audio_queue"):
                recognizer.audio_queue.put(data)

    # --- SpeechRecognizerDelegate ---

    async def speech_recognizer_did_receive_final_result(self, result: str | LocaleString):
        from stark.models.voice_transcription_string import VoiceTranscriptionString

        # extract track from VoiceTranscriptionString if available
        if isinstance(result, VoiceTranscriptionString) and result.track:
            track = result.track
            lang = track.language_code
        else:
            lang = result.language_code if isinstance(result, LocaleString) else "base"
            track = VoiceTranscriptionTrack(text=str(result), language_code=lang)

        transcription = Transcription(best=track, origins={lang: track})

        current = self._current_transcription or transcription
        self._current_transcription = current
        current.origins.update(transcription.origins)

        # wait for other languages to report
        start_time = time.monotonic()
        expected_languages = {sr.language_code for sr in self._speech_recognizers if hasattr(sr, "language_code")}

        while (
            current.origins.keys() != expected_languages and time.monotonic() - start_time < self._convergence_timeout
        ):
            await anyio.sleep(0.01)

        if not self._current_transcription:
            return
        self._current_transcription = None

        # build best confidence track; language priority follows recognizer order
        language_priority = {
            sr.language_code: i for i, sr in enumerate(self._speech_recognizers) if hasattr(sr, "language_code")
        }
        tracks = {track.model_copy(deep=True) for track in current.origins.values()}
        current.best = self._build_best_confidence(tracks, language_priority=language_priority)
        current.best.language_code = "base"

        # emit as VoiceTranscriptionString
        vts = current.to_voice_transcription_string()

        if delegate := self.delegate:
            await delegate.speech_recognizer_did_receive_final_result(vts)

    async def speech_recognizer_did_receive_partial_result(self, result: str):
        if delegate := self.delegate:
            await delegate.speech_recognizer_did_receive_partial_result(result)

    async def speech_recognizer_did_receive_empty_result(self):
        if delegate := self.delegate:
            await delegate.speech_recognizer_did_receive_empty_result()

    # --- private ---

    def _build_best_confidence(
        self,
        tracks: set[VoiceTranscriptionTrack],
        until: float | None = None,
        language_priority: dict[str, int] | None = None,
    ) -> VoiceTranscriptionTrack:
        if not tracks:
            return VoiceTranscriptionTrack()
        language_priority = language_priority or {}

        best = VoiceTranscriptionTrack()

        while tracks:
            tracks = set(
                filter(
                    lambda track: track.result and (until is None or track.result[0].middle < until),
                    tracks,
                )
            )

            if not tracks:
                break

            longest = max(
                tracks,
                key=lambda track: track.result[0].end if until is None or track.result[0].middle < until else 0,
            )
            end = min(longest.result[0].end, until) if until is not None else longest.result[0].end
            other = self._build_best_confidence(tracks - {longest}, until=end, language_priority=language_priority)

            base_word = longest.result.pop(0)
            alternative_words = list(self._pop_words_until_time(other, end))

            if not alternative_words:
                best.result.append(base_word)
                continue

            complex_alt = VoiceTranscriptionWord(
                word=" ".join(w.word for w in alternative_words),
                language_code=alternative_words[0].language_code,
                char_start=0,
                char_end=0,
                start=min(w.start for w in alternative_words),
                end=max(w.end for w in alternative_words),
                conf=sum(w.conf or 0 for w in alternative_words) / len(alternative_words),
            )

            base_conf = base_word.conf or 0
            alt_conf = complex_alt.conf or 0

            if base_conf == alt_conf:
                # equal confidence: prefer the language with higher priority (lower index in recognizer list)
                base_priority = language_priority.get(base_word.language_code, 999)
                alt_priority = language_priority.get(complex_alt.language_code, 999)
                best.result.append(base_word if base_priority <= alt_priority else complex_alt)
            elif base_conf > alt_conf:
                best.result.append(base_word)
            else:
                best.result.append(complex_alt)

        best.text = " ".join(w.word for w in best.result)
        return best

    def _pop_words_until_time(
        self, track: VoiceTranscriptionTrack, until: float
    ) -> Generator[VoiceTranscriptionWord, None, None]:
        while track.result and track.result[0].middle <= until:
            yield track.result.pop(0)
