# Speech Recognition (STT)

Turning spoken audio into text is a problem on its own, useful even if you never touch the rest of S.T.A.R.K. This page covers S.T.A.R.K.'s speech-recognition layer: the protocol it's built around, ready-to-use implementations, and how to plug in your own engine.

S.T.A.R.K. defines the protocol so any backend is a drop-in replacement inside S.T.A.R.K. itself, but the protocol is deliberately agnostic, not tied to the rest of the framework. Wrap any STT engine behind it and you get the same drop-in swappability in any other Python project, with a couple of ready-made implementations included out of the box.

## Use it standalone

`SpeechRecognizer` implementations don't require `CommandsManager` or any other part of the framework, they're a thin, swappable interface around an STT engine.

```python
from stark.interfaces.vosk import VoskSpeechRecognizer

recognizer = VoskSpeechRecognizer(model_url='...')  # pick a model: https://alphacephei.com/vosk/models

class PrintResults:
    async def speech_recognizer_did_receive_final_result(self, result: str):
        print('Final:', result)
    async def speech_recognizer_did_receive_partial_result(self, result: str):
        print('Partial:', result)
    async def speech_recognizer_did_receive_empty_result(self):
        pass

recognizer.delegate = PrintResults()
await recognizer.start_listening()  # transcribes the microphone, no commands involved
```

Want it wired into a full assistant? See [How to Run](https://stark.markparker.me/how-to-run/index.md).

## Ready Implementations

### `VoskSpeechRecognizer`

Offline speech recognition via the [Vosk](https://alphacephei.com/vosk/) library. Downloads and caches the chosen model on first use; no internet required after that.

```python
VoskSpeechRecognizer(model_url: str, language_code: str | None = None, speaker_model_url: str | None = None)
```

Pass `speaker_model_url` to enable speaker-embedding extraction (used for cross-recognizer matching when running [multiple languages simultaneously](https://stark.markparker.me/voice-assistant/#multi-language-voice-setup), not yet used for diarization, but the data is captured).

## The Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SpeechRecognizerDelegate(Protocol):
    async def speech_recognizer_did_receive_final_result(self, result: str): pass
    async def speech_recognizer_did_receive_partial_result(self, result: str): pass
    async def speech_recognizer_did_receive_empty_result(self): pass

@runtime_checkable
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    delegate: SpeechRecognizerDelegate | None

    async def start_listening(self): pass
    def stop_listening(self): pass
```

- **`SpeechRecognizerDelegate`** receives the results: a final transcript, an interim/partial transcript (useful for live captions or barge-in detection), or a signal that nothing was heard.
- **`SpeechRecognizer`** is the input side: `start_listening`/`stop_listening` control the mic (or whatever audio source you point it at), and `is_recognizing` reports current state.

## Implementing Your Own

Any class that satisfies the `SpeechRecognizer` protocol is a drop-in replacement, pass it to `run()` exactly like `VoskSpeechRecognizer`. Use the actual `VoskSpeechRecognizer` source as a reference implementation:

This is exactly where a cloud STT backend (Whisper API, Google Speech-to-Text, Azure) or a different offline engine would plug in, and a great first contribution if one doesn't exist yet. See [Roadmap](https://stark.markparker.me/roadmap/index.md).
