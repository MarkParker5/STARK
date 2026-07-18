---
description: S.T.A.R.K. is a modern, async Python framework for building voice assistants and natural language interfaces. Offline-first, multilingual by design, no AI required. Think FastAPI, but for speech.
---

# Welcome to S.T.A.R.K.

!!! info "~40 minutes, start to finish"

    This entire docs site reads sequentially, like a book, in about half an hour. Worth the full read: there are features in here (nested contexts, background commands, phonetic matching) you might not know you want yet.

!!! warning "Active Development"

    S.T.A.R.K. is under active development. Most core features (commands, patterns, contexts, multilingual parsing) are stable and tested. A few, like cross-language multi-command matching, are still experimental. Found something rough? [Tell us in Discussions](https://github.com/MarkParker5/STARK/discussions); feedback shapes what gets stabilized next.

!!! tip "LLM-Friendly Docs"

    Building with S.T.A.R.K. using an AI coding assistant? Point it at the machine-readable docs:

    - [`/llms.txt`](/llms.txt), page index with descriptions
    - [`/llms-full.txt`](/llms-full.txt), complete documentation in a single file

## Speech and Text Algorithmic Recognition Kit

S.T.A.R.K. is a modern, async Python framework for building voice assistants and natural language interfaces. Think of it as [FastAPI](https://fastapi.tiangolo.com/), but for speech instead of HTTP.

No need to build alone. See [Get Involved](#get-involved) below.

New to S.T.A.R.K.? The nav on the left reads sequentially, start to finish, like a book, not a reference dump.

---

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

1. Register a command with `@manager.new(...)`. The string is the pattern S.T.A.R.K. matches against what the user says. More in [Creating Commands](creating-commands.md).
2. Pick a speech recognizer and synthesizer. S.T.A.R.K. ships ready-to-use offline ones; see [Default Speech Interfaces](default-speech-interfaces.md).
3. `run()` wires everything together and starts listening. This is the whole assistant: five lines of actual logic.

That's a complete, working voice assistant: no cloud calls, no API keys, runs fully offline. Prefer text in a terminal over a microphone? See [How to Run](how-to-run.md) for the no-audio variant.

## Patterns parse parameters too

```py
@manager.new('hello $name:Word')
def hello(name: str) -> Response:
    return Response(f'Hello, {name}!')

# "hello Mark" -> "Hello, Mark!"
# "hello Archie" -> "Hello, Archie!"
```

Patterns aren't fixed phrases. `$name:Word` extracts a parameter and hands it straight to your function, typed and ready to use, no parsing code of your own. Full syntax in [Patterns](patterns.md).

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

S.T.A.R.K.'s pattern matcher parses multiple commands out of one utterance on its own, even when they're phrased back-to-back. Most voice assistants still can't do that, even today.

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

1. Responds immediately and offers a `stop timer` command, scoped to this context only. It won't show up anywhere else. The nested-context mechanics behind this are in [Commands Context](commands-context.md).
2. Keeps running in the background: four checkpoints, 15 seconds apart, a minute total. The assistant is free to handle other input the whole time, it's not blocked waiting on this command.
3. A plain global flag is enough to cancel it, no extra machinery needed. If your command needs local state instead of a shared flag, define `stop_timer` inside `start_timer` so it closes over the same variables.

This pattern, immediate response, async progress updates, an optional cancel command, is what powers timers, downloads, or any long-running task. Full walkthrough in [Sync vs Async Commands](sync-vs-async-commands.md#background-commands).

---

## What Makes S.T.A.R.K. Different

- **4 required dependencies**: `pydantic`, `asyncer`, `anyio`, `numpy`. Everything else (STT/TTS backends, NLP libraries) is opt-in. See [Installation](installation.md).
- **No AI required**: pattern, phonetic, and fuzzy matching are deterministic, fast, and explainable. LLM integration is opt-in, not a dependency. See [Fallback Command / LLM Integration](advanced/fallback-command-llm-integration.md) and where this is headed in [AI Agent Platform](agent-platform.md).
- **Multilingual by design**: including commands that mix languages mid-sentence. See [Going Multilingual](localization-and-multilingual/index.md).
- **Phonetic and fuzzy matching**: misspellings, accents, and cross-language name lookup, handled out of the box. See [Tools](tools/index.md).
- **Nested contexts**: multi-level menus, follow-ups, and stateful conversations, not just one-shot Q&A. See [Commands Context](commands-context.md).
- **Background commands & multiple responses**: fire a task, keep listening, get notified as it progresses. See [Sync vs Async Commands](sync-vs-async-commands.md#background-commands).
- **Assistant modes**: active, waiting, inactive, sleeping (wake-word), explicit, and external-trigger modes, all configurable. See [Running Your Assistant](running-your-assistant.md).
- **Modular by design**: swap commands, processors, type parsers, or the entire IO layer (voice, text, a [Telegram bot](advanced/custom-interfaces.md#telegram-bot), your own). See [How to Run](how-to-run.md).
- **100% on-device**: runs fully offline, your data stays yours.

!!! note "Coming in v5: AI Agent Platform"

    The next major release adds an optional layer for building agents on top of S.T.A.R.K.'s existing background commands and LLM integration, without changing anything that already works. [Read the early plan →](agent-platform.md)

## Powered By STARK

[Archie](https://majordom.io), the voice assistant built for [MajorDom](https://majordom.io), runs on S.T.A.R.K.: nested contexts for device control, multilingual input, fully offline operation.

## Minimal Dependencies

| Required | Optional (install as needed) |
|---|---|
| `pydantic` | `sounddevice`, `soundfile`, audio IO |
| `asyncer` | `vosk`, offline speech recognition |
| `anyio` | `torch`, Silero speech synthesis |
| `numpy` | `google-cloud-texttospeech`, cloud TTS |
| | `spacy`, NER pre-processing |

```bash
pip install stark-engine          # core only
pip install stark-engine[vosk]    # + offline STT
pip install stark-engine[silero]  # + offline TTS
pip install stark-engine[all]     # everything
```

See [Installation](installation.md) for the full breakdown.

## Get Involved

S.T.A.R.K. grows through the people building with it. A few ways to plug in:

- 💬 **[Discussions](https://github.com/MarkParker5/STARK/discussions)**: ask questions, report what's confusing, show off what you built, and collaborate. We need all the feedback we can get to make S.T.A.R.K. better, so no idea is too small to share, and don't be afraid to be first, every thread starts empty.
- 📦 **[STARK-PLACE](contributing-and-shared-usage-stark-place.md)**: the community command library. Use what others built, or contribute your own.
- 🐛 **[Issues](https://github.com/MarkParker5/STARK/issues)**: found a bug? Let us know.
- 💡 **[Project Ideas](project-ideas.md)**: looking for something to build? Start here.

There's no official Discord or Telegram, and that's intentional. If you want a non-github chat group, start one and link it in [Collaboration Discussion](https://github.com/MarkParker5/STARK/discussions/17) post. Self-organized communities are welcome, just keep Discussions as the canonical place new people land.

---

## License

The S.T.A.R.K. project is licensed under the [CC BY-NC-SA 4.0 International license](https://github.com/MarkParker5/STARK/tree/master/LICENSE.md). You're welcome to modify, contribute to the repository, create, and share forks. Just remember to attribute the original repository and its creator, abstain from commercial use, and retain the existing license.

**Note**: Failing to provide the necessary attribution or using the project for commercial purposes breaches the licensing terms and could have legal consequences.

Want to use S.T.A.R.K. commercially, or talk about a partnership? Joint projects, hardware, contract development, anything related. Reach out via [parker-industries.org/partnership](https://parker-industries.org/partnership). We're genuinely open to it.
