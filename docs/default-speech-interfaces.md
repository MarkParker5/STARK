# Default Speech Interfaces

`run()` needs a speech recognizer and a speech synthesizer, this page is the quick reference for wiring up the ones S.T.A.R.K. ships. The Vosk + Silero stack isn't fixed: both are protocol-based, so any backend that implements the same thin interface is a drop-in replacement, more native alternatives are on the way (see [Roadmap](roadmap.md)), and nothing stops you from wiring in your own today. For the underlying protocols, what each method does, and how to implement your own backend, see [Speech Recognition (STT)](tools/speech-recognition.md) and [Speech Synthesis (TTS)](tools/speech-synthesis.md), both work standalone too, without any other part of the framework.

## Recognizers

### `VoskSpeechRecognizer`

Offline recognition via [Vosk](https://alphacephei.com/vosk/). Downloads and caches the model on first use.

```python
VoskSpeechRecognizer(model_url: str, language_code: str | None = None, speaker_model_url: str | None = None)
```

## Synthesizers

### `SileroSpeechSynthesizer`

Offline synthesis via [Silero](https://github.com/snakers4/silero-models).

```python
SileroSpeechSynthesizer(model_url: str, speaker: str = 'baya', threads: int = 4, device='cpu', torch_backends_quantized_engine: str = 'qnnpack')
```

### `GCloudSpeechSynthesizer`

Cloud synthesis via Google Cloud Text-to-Speech, requires credentials configured ahead of time.

```python
GCloudSpeechSynthesizer(voice_name: str, language_code: str, json_key_path: str)
```

## Putting Them Together

```python
import anyio
from stark import run, CommandsManager
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.interfaces.silero import SileroSpeechSynthesizer

manager = CommandsManager()
# ... register commands ...

async def main():
    recognizer = VoskSpeechRecognizer(model_url='...')
    synthesizer = SileroSpeechSynthesizer(model_url='...')
    await run(manager, recognizer, synthesizer)

anyio.run(main)
```

This is the same pattern as the front-page [Hello, Stark!](index.md#hello-stark) example. Required dependencies (`vosk`, `sounddevice`, `torch`, etc.) are install extras, see [Installation](installation.md).

For everything else `run()` accepts (custom processors, a localizer, multiple recognizers for multilingual setups), see [How to Run](how-to-run.md). For a fundamentally different IO layer that isn't voice at all, see [Custom IO & Context Delegate](advanced/custom-interfaces.md).
