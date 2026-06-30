# How to Run

There are several ways to get a S.T.A.R.K. assistant running, from "just call one function" to "build your own IO layer from scratch." This page covers them in order, from least to most control.

## 1. Defaults: `run()`

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

This is the one-call path used on the [front page](index.md#hello-stark): `run()` builds a `CommandsContext`, wires up a `VoiceAssistant`, starts the microphone, and starts listening. For most assistants, this is all you need.

## 2. Custom Overrides

`run()`'s full signature:

```python
async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer | list[SpeechRecognizer],
    speech_synthesizer: SpeechSynthesizer,
    processors: list[CommandsContextProcessor] | None = None,
    localizer: Localizer | None = None,
):
```

- **`processors`**: override the default pattern-matching pipeline. Omit it and `run()` picks `SearchProcessor` alone, or `CorrectionsProcessor` + `SearchProcessor` if you pass a `localizer`. See [Custom Processors](advanced/custom-processors.md) to add your own stage (NER, custom corrections, anything that needs to run before or after matching).
- **`localizer`**: enables multilingual parsing and pulls in `CorrectionsProcessor` by default. See [Going Multilingual](localization-and-multilingual/index.md).
- **`speech_recognizer` as a list**: pass more than one recognizer (e.g. one per language) and `run()` automatically wraps them in a `SpeechRecognizerRelay`, which compares per-word confidence across recognizers and assembles the best transcription. See [Voice Assistant & Modes, Multi-Language Voice Setup](voice-assistant.md#multi-language-voice-setup).

## 3. Your Own Minimal Assembly Function

`run()` is opinionated: it always wires a `VoiceAssistant`, always starts a microphone. If you want a different IO source entirely, text in a terminal, no audio at all, skip `run()` and construct `CommandsContext` directly:

```python
import sys
import anyio
from stark.core import CommandsContext, CommandsManager, Response

manager = CommandsManager()

@manager.new('hello')
async def hello_command() -> Response:
    return Response('Hello, Stark!')

async def main():
    async with anyio.create_task_group() as task_group:
        context = CommandsContext(task_group=task_group, commands_manager=manager)  # 1
        context.delegate = TextDelegate()                                           # 2

        for line in sys.stdin:                                                       # 3
            await context.process_string(line.strip())

anyio.run(main)
```

1. No recognizer, no synthesizer, no microphone, `CommandsContext` alone is the whole engine.
2. `TextDelegate` just needs to satisfy `CommandsContextDelegate`, a full, runnable implementation (print responses to the terminal) is in [Custom IO & Context Delegate, A Minimal Custom Delegate](advanced/custom-interfaces.md#a-minimal-custom-delegate).
3. Feed it text however you like, reading stdin here, but it could just as easily be a GUI event handler or an incoming HTTP request.

This is the no-audio, IO-less path, same mechanics as the voice version, minus speech entirely. Good for testing, debugging, or text-first interfaces.

## 4. The Full Default `run()`, for Reference

Want to see exactly what `run()` does internally, every task it starts, every delegate it wires, so you can replicate and extend it yourself? See [Custom Run](advanced/custom-run.md) in Going Deeper; it walks through the real implementation line by line.

## IO Options at a Glance

| Interface | Status | Where |
|---|---|---|
| **VUI** (voice) | Built-in | `VoiceAssistant`, via `run()`, see above |
| **TUI** (terminal text) | Built-in pattern | The minimal example above, or `STARK_VOICE_CLI=1` on top of `VoiceAssistant`, see [Voice Assistant & Modes](voice-assistant.md) |
| **GUI** | Not yet built | A great first contribution, see [Custom IO & Context Delegate](advanced/custom-interfaces.md#gui) for the shape it would take, and [Roadmap](roadmap.md) |
| **API** | Not yet built | Same as GUI, `CommandsContextDelegate` is the integration point |

## 5. Two Levels of Customization

Once you're running an assistant, there are two ways to hook into its behavior, depending on how much you need to change:

**Simpler, subclass `VoiceAssistant`.** Override a lifecycle method, call `super()`, add your logic. Good for things like updating a GUI alongside voice, or logging every response. See [Voice Assistant & Modes, Customizing VA and Observing Events](voice-assistant.md#customizing-va-and-observing-events).

**Full control, implement `CommandsContextDelegate` yourself.** This is the protocol `VoiceAssistant` itself implements. Skip `VoiceAssistant` entirely and you control the whole IO loop, this is what step 3 above does. See [Custom IO & Context Delegate](advanced/custom-interfaces.md) for the protocol and worked example.

---

Building something with a custom IO layer? [Share it in Discussions](https://github.com/MarkParker5/STARK/discussions) or contribute it to [STARK-PLACE](contributing-and-shared-usage-stark-place.md), GUI and API interfaces especially are open ground.
