# Hello World

Congratulations on installing S.T.A.R.K.! This guide walks through your first voice-driven application: a command that responds to "hello" by saying "Hello, Stark!" back. ([jump to async commands →](https://stark.markparker.me/creating-commands/#async-commands))

## Hello, Stark!

S.T.A.R.K. doesn't lock you into one speech engine, it's built around protocols, so any recognizer or synthesizer that implements them works. This tutorial uses Vosk for speech recognition and Silero for speech synthesis, both fully offline. Both download and cache their models automatically on first use:

- [Vosk models](https://alphacephei.com/vosk/models), pick one for your language
- [Silero models](https://github.com/snakers4/silero-models?tab=readme-ov-file#models-and-speakers), pick a voice

```py
import anyio
from stark import run, CommandsManager, Response
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.interfaces.silero import SileroSpeechSynthesizer


VOSK_MODEL_URL = "YOUR_CHOSEN_VOSK_MODEL_URL"
SILERO_MODEL_URL = "YOUR_CHOSEN_SILERO_MODEL_URL"

manager = CommandsManager()                                         # 1

@manager.new('hello')                                                # 2
def hello_command() -> Response:
    return Response('Hello, Stark!', voice='Hello, Stark!')     # 3

async def main():
    recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)      # 4
    synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL)
    await run(manager, recognizer, synthesizer)                      # 5

if __name__ == '__main__':
    anyio.run(main)
```

1. `CommandsManager` is where every command your assistant understands gets registered.
1. `@manager.new('hello')` registers a command matched against the pattern `'hello'`. Patterns can get much more dynamic than a literal word, see [Patterns](https://stark.markparker.me/patterns/index.md).
1. A `Response` carries both the spoken (`voice`) and displayed (`text`) reply, they don't have to match, but here they do. Plenty of other fields exist (status, follow-up commands, parameters), see [Command Response](https://stark.markparker.me/command-response/index.md) in Core Concepts.
1. Pick a recognizer and synthesizer. These two are offline; S.T.A.R.K. doesn't require any cloud service or API key to work.
1. `run()` wires the manager, recognizer, and synthesizer together and starts listening. Say "hello," hear "Hello, Stark!" back.

This command is declared plain `def`, simplest option, and S.T.A.R.K. handles the rest. Once you start awaiting things inside a command, you'll want `async def` instead, see [Async Commands](https://stark.markparker.me/creating-commands/#async-commands) and [Sync vs Async Commands](https://stark.markparker.me/sync-vs-async-commands/index.md) for when to reach for which.

Prefer to skip the microphone for now and type input in a terminal instead? See [How to Run](https://stark.markparker.me/how-to-run/index.md) for the no-audio variant of this same example.
