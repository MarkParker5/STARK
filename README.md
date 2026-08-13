<!-- flagship → markparker.me -->
<a href="https://markparker.me" target="_blank">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://markparker.me/banners/flagship-dark.webp"
    />
    <img
      alt="A Mark Parker project — see more at markparker.me"
      src="https://markparker.me/banners/flagship-light.webp"
    />
  </picture>
</a>

# S.T.A.R.K.

<!-- banner
![S.T.A.R.K. - Speech and Text Advanced Recognition Kit](https://markparker.me/projects/stark.webp) -->

**Speech and Text Advanced Recognition Kit**: a modern, async Python framework for building voice assistants and natural language interfaces. Think [FastAPI](https://fastapi.tiangolo.com/), but for speech instead of HTTP.

No need to build alone. See [Get Involved](#community) below.

## What Makes S.T.A.R.K. Different

- **100% on-device**: runs fully offline, no cloud dependencies. Your data stays yours. Doesn't stop working when internet connection is lost.
- **4 required dependencies**: `pydantic`, `asyncer`, `anyio`, `numpy`. Everything else (STT/TTS backends, NLP libraries) is opt-in. See [Installation](getting-started/installation.md).
- **No AI required**: pattern, phonetic, and fuzzy matching are deterministic, fast, and explainable. LLM integration is opt-in, not a dependency. See [Fallback Command / LLM Integration](advanced/fallback-command-llm-integration.md) and where this is headed in [AI Agent Platform](agent-platform.md).
- **Phonetic and fuzzy matching**: misspellings, accents, and cross-language name lookup, handled out of the box. See [Tools](tools/index.md).
- **Multilingual by design**: including commands that mix languages mid-sentence. See [Going Multilingual](localization-and-multilingual/index.md).
- **Nested contexts**: multi-level menus, follow-ups, and stateful conversations, not just one-shot Q&A. See [Commands Context](core-concepts/commands-context.md).
- **Background commands & multiple responses**: fire a task, keep listening, get notified as it progresses. See [Sync vs Async Commands](core-concepts/sync-vs-async-commands.md#background-commands).
- **Assistant modes**: active, waiting, inactive, sleeping (wake-word), explicit, and external-trigger modes, all configurable. See [Running Your Assistant](running/index.md).
- **Modular by design**: swap commands, processors, type parsers, or the entire IO layer (voice, text, a [Telegram bot](running/custom-interfaces.md#telegram-bot), your own). See [How to Run](running/how-to-run.md).
- **STARK-PLACE**: the extension ecosystem — installable packages and copy-paste examples built on S.T.A.R.K. Use what others made, or share your own.

## Quick Start

```bash
pip install stark-engine
```

Full docs, including installation options and extras, at **[stark.markparker.me](https://stark.markparker.me/)**.

## Hello, Stark!

```py
import anyio
from stark import run, CommandsManager, Response
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.interfaces.silero import SileroSpeechSynthesizer

VOSK_MODEL_URL = '...'    # pick one: https://alphacephei.com/vosk/models
SILERO_MODEL_URL = '...'  # pick one: https://github.com/snakers4/silero-models

manager = CommandsManager()

@manager.new('hello')                                                       # 1
def hello_command() -> Response:
    return Response('Hello, Stark!')

async def main():
    recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)             # 2
    synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL)
    await run(manager, recognizer, synthesizer)                            # 3

if __name__ == '__main__':
    anyio.run(main)
```

1. Register a command with `@manager.new(...)`. The string is the pattern STARK matches against what the user says.
2. Pick a speech recognizer and synthesizer. STARK ships ready-to-use ones (offline Vosk + Silero here); see [Default Speech Interfaces](https://stark.markparker.me/running/default-speech-interfaces/).
3. `run()` wires everything together and starts listening. This is the whole assistant.

That's a complete, working voice assistant: no cloud, no API keys. Want text-only, no microphone needed? See [How to Run](https://stark.markparker.me/running/how-to-run/).

## Patterns parse parameters too

```py
@manager.new('hello $name:NLWord')
def hello(name: str) -> Response:
    return Response(f'Hello, {name}!')

# "hello Mark" -> "Hello, Mark!"
# "hello Archie" -> "Hello, Archie!"
```

Patterns aren't fixed phrases. `$name:NLWord` extracts a parameter and hands it straight to your function, typed and ready to use. See [Patterns](https://stark.markparker.me/core-concepts/patterns/).

## One sentence, multiple commands

```py
# user says: "turn off the light and play some music"

@manager.new('turn off the light')
def lights_off() -> Response:
    return Response('Lights off.')

@manager.new('play (some|the) music')
def play_music() -> Response:
    return Response('Playing music.')

# both commands fire from that single sentence, no extra wiring required
```

STARK's pattern matcher parses multiple commands out of one utterance on its own, even across two separate phrases stitched together. Most voice assistants still can't do that.

## Background commands

```py
import anyio
from stark.core import AsyncResponseHandler

timer_cancelled = False

@manager.new('start timer')
async def start_timer(handler: AsyncResponseHandler) -> Response:
    global timer_cancelled
    timer_cancelled = False
    await handler.respond(Response('Timer started.', commands=[stop_timer]))  # 1
    for percent in (25, 50, 75, 100):
        await anyio.sleep(15)                                                       # 2
        if timer_cancelled:
            return Response('Timer stopped.')                                  # 3
        await handler.respond(Response(f'Timer {percent}% done.'))
    return Response('Timer finished!')

@manager.new('stop timer', hidden=True)
async def stop_timer(handler: AsyncResponseHandler) -> Response:
    global timer_cancelled
    timer_cancelled = True
    handler.pop_context()
    return Response('Stopping timer...')
```

1. Responds immediately and offers a `stop timer` command, scoped to this context only. It won't show up anywhere else.
2. Keeps running in the background: four checkpoints, 15 seconds apart, a minute total. The assistant is free to handle other input the whole time.
3. A plain global flag is enough to cancel it, no extra machinery needed. (If your command needs local state instead of a shared flag, define `stop_timer` inside `start_timer` so it closes over the same variables.)

This pattern, immediate response, async progress updates, an optional cancel command, is what powers timers, downloads, or any long-running task. See [Sync vs Async Commands](https://stark.markparker.me/core-concepts/sync-vs-async-commands/#background-commands) and [Commands Context](https://stark.markparker.me/core-concepts/commands-context/).

## Powered by STARK

[Archie](https://majordom.io), the voice assistant built for [MajorDom](https://majordom.io), runs on STARK: nested contexts for device control, multilingual input, fully offline.

## Community

- 💬 [Discussions](https://github.com/MarkParker5/STARK/discussions): questions, feedback, showcase what you built. We need all the feedback we can get to make STARK better, so don't be afraid to be first, every thread starts empty.
- 📦 [STARK-PLACE](https://stark.markparker.me/ecosystem/): the extension ecosystem — installable packages (`stark-ai`, `stark-triggers`, `stark-devtools`) and copy-paste examples built on STARK
- 🐛 [Issues](https://github.com/MarkParker5/STARK/issues): found a bug?

## License

The S.T.A.R.K. project is licensed under the [PolyForm Noncommercial License 1.0.0](https://github.com/MarkParker5/STARK/tree/master/LICENSE.md). You're welcome to modify, contribute to the repository, create, and share forks. Just remember to attribute the original repository and its creator, abstain from commercial use, and retain the existing license.

Want to use STARK commercially, or talk about a partnership? Joint projects, hardware, contract development, anything related. Reach out via [parker-industries.org/partnership](https://parker-industries.org/partnership). We're genuinely open to it.
