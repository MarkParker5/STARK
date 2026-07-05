# Speech Synthesis (TTS)

Turning text into spoken audio is a problem on its own, useful even if you never touch the rest of S.T.A.R.K. This page covers S.T.A.R.K.'s speech-synthesis layer: the protocol it's built around, ready-to-use implementations, and how to plug in your own engine.

S.T.A.R.K. defines the protocol so any backend is a drop-in replacement inside S.T.A.R.K. itself, but the protocol is deliberately agnostic, not tied to the rest of the framework. Wrap any TTS engine behind it and you get the same drop-in swappability in any other Python project, with a couple of ready-made implementations included out of the box.

## Use it standalone

`SpeechSynthesizer` implementations don't require `CommandsManager` or any other part of the framework, they're a thin, swappable interface around a TTS engine.

```python
from stark.interfaces.silero import SileroSpeechSynthesizer

synthesizer = SileroSpeechSynthesizer(model_url='...')  # pick a model: https://github.com/snakers4/silero-models
result = await synthesizer.synthesize('Hello, Stark!')
await result.play()  # plays through your default audio output, no commands involved
```

Want it wired into a full assistant? See [How to Run](https://stark.markparker.me/how-to-run/index.md).

## Ready Implementations

### `SileroSpeechSynthesizer`

Offline synthesis via [Silero](https://github.com/snakers4/silero-models) models.

```python
SileroSpeechSynthesizer(
    model_url: str,
    speaker: str = 'baya',
    threads: int = 4,
    device: str = 'cpu',
    torch_backends_quantized_engine: str = 'qnnpack',
)
```

### `GCloudSpeechSynthesizer`

Cloud synthesis via Google Cloud Text-to-Speech. Requires credentials configured ahead of time.

```python
GCloudSpeechSynthesizer(voice_name: str, language_code: str, json_key_path: str)
```

## The Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SpeechSynthesizerResult(Protocol):
    async def play(self): pass

@runtime_checkable
class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str) -> SpeechSynthesizerResult: pass
```

- **`SpeechSynthesizer`** takes text and returns a result object, synthesis and playback are separate steps, so you can synthesize ahead of time, queue results, or route audio elsewhere instead of playing immediately.
- **`SpeechSynthesizerResult`** wraps whatever the backend produced and knows how to play itself via `play()`.

## Implementing Your Own

Any class that satisfies the `SpeechSynthesizer` protocol is a drop-in replacement, pass it to `run()` exactly like `SileroSpeechSynthesizer`. Use the actual `SileroSpeechSynthesizer` source as a reference implementation:

This is exactly where another cloud TTS backend (ElevenLabs, Azure, Amazon Polly) or a different offline engine would plug in, and a great first contribution if one doesn't exist yet. See [Roadmap](https://stark.markparker.me/roadmap/index.md).
