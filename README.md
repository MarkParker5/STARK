# S.T.A.R.K.

**Speech and Text Algorithmic Recognition Kit**: a modern, async Python framework for building voice assistants and natural language interfaces. Think [FastAPI](https://fastapi.tiangolo.com/), but for speech instead of HTTP.

No need to build alone. See [Get Involved](#community) below.

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
2. Pick a speech recognizer and synthesizer. STARK ships ready-to-use ones (offline Vosk + Silero here); see [Default Speech Interfaces](https://stark.markparker.me/default-speech-interfaces/).
3. `run()` wires everything together and starts listening. This is the whole assistant.

That's a complete, working voice assistant: no cloud, no API keys. Want text-only, no microphone needed? See [How to Run](https://stark.markparker.me/how-to-run/).

## Patterns parse parameters too

```py
@manager.new('hello $name:Word')
def hello(name: str) -> Response:
    return Response(f'Hello, {name}!')

# "hello Mark" -> "Hello, Mark!"
# "hello Archie" -> "Hello, Archie!"
```

Patterns aren't fixed phrases. `$name:Word` extracts a parameter and hands it straight to your function, typed and ready to use. See [Patterns](https://stark.markparker.me/patterns/).

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

This pattern, immediate response, async progress updates, an optional cancel command, is what powers timers, downloads, or any long-running task. See [Sync vs Async Commands](https://stark.markparker.me/sync-vs-async-commands/#background-commands) and [Commands Context](https://stark.markparker.me/commands-context/).

## Why STARK

- **4 required dependencies**: `pydantic`, `asyncer`, `anyio`, `numpy`. Everything else (STT/TTS backends, NLP) is opt-in. See [Installation](https://stark.markparker.me/installation/).
- **No AI required**: pattern, phonetic, and fuzzy matching are deterministic and fast. LLM integration is opt-in, not a dependency. See [Fallback Command / LLM Integration](https://stark.markparker.me/advanced/fallback-command-llm-integration/) and where this is headed in [AI Agent Platform](https://stark.markparker.me/agent-platform/).
- **Multilingual by design**: including commands that mix languages mid-sentence.
- **Phonetic and fuzzy matching**: misspellings, accents, and cross-language name lookup, handled out of the box. See [Tools](https://stark.markparker.me/tools/).
- **Nested contexts**: multi-level menus, follow-ups, and stateful conversations. See [Commands Context](https://stark.markparker.me/commands-context/).
- **Background commands & multiple responses**: fire a task, keep listening, get notified as it progresses. See [Sync vs Async Commands](https://stark.markparker.me/sync-vs-async-commands/#background-commands).
- **Assistant modes**: active, waiting, inactive, sleeping (wake-word), explicit, and external-trigger modes. See [Running Your Assistant](https://stark.markparker.me/running-your-assistant/).
- **Modular by design**: swap commands, processors, type parsers, or the entire IO layer (voice, text, a [Telegram bot](https://stark.markparker.me/advanced/custom-interfaces/#telegram-bot), your own). See [How to Run](https://stark.markparker.me/how-to-run/).
- **100% on-device**: runs fully offline, your data stays yours.

## Powered by STARK

[Archie](https://majordom.io), the voice assistant built for [MajorDom](https://majordom.io), runs on STARK: nested contexts for device control, multilingual input, fully offline.

## Quick start

```bash
pip install stark-engine
```

Full docs, including installation options and extras, at **[stark.markparker.me](https://stark.markparker.me/)**.

## Community

- 💬 [Discussions](https://github.com/MarkParker5/STARK/discussions): questions, feedback, showcase what you built. We need all the feedback we can get to make STARK better, so don't be afraid to be first, every thread starts empty.
- 📦 [STARK-PLACE](https://github.com/MarkParker5/STARK-PLACE): community commands and reference implementations
- 🐛 [Issues](https://github.com/MarkParker5/STARK/issues): found a bug?

## License

The S.T.A.R.K. project is licensed under the [CC BY-NC-SA 4.0 International license](https://github.com/MarkParker5/STARK/tree/master/LICENSE.md). You're welcome to modify, contribute to the repository, create, and share forks. Just remember to attribute the original repository and its creator, abstain from commercial use, and retain the existing license.

Want to use STARK commercially, or talk about a partnership? Joint projects, hardware, contract development, anything related. Reach out via [parker-industries.org/partnership](https://parker-industries.org/partnership). We're genuinely open to it.
