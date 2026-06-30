# Custom Run

`run()` is opinionated, it always wires a `VoiceAssistant`, always starts the microphone, always uses the default processor pipeline unless told otherwise (see [How to Run](../how-to-run.md) for the parameters it does expose). Most of the time, those defaults are exactly right. When they're not, you want a different startup sequence, extra concurrent tasks, custom logging baked into the assembly itself, replicate `run()` and adjust it, rather than fighting its assumptions from the outside.

This page walks through what `run()` actually does, so a custom version isn't guesswork.

## Understanding the Default Run Function

```python
import asyncer

from stark.core import CommandsContext, CommandsManager
from stark.core.health_check import health_check
from stark.core.processors.search_processor import SearchProcessor
from stark.general.blockage_detector import BlockageDetector
from stark.interfaces.microphone import Microphone
from stark.interfaces.protocols import SpeechRecognizer, SpeechSynthesizer
from stark.voice_assistant import VoiceAssistant


async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer,
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(                                          # 1
            task_group=main_task_group,
            commands_manager=manager,
            processors=[SearchProcessor()],
        )

        voice_assistant = VoiceAssistant(                                   # 2
            speech_recognizer=speech_recognizer,
            speech_synthesizer=speech_synthesizer,
            commands_context=context,
        )
        speech_recognizer.delegate = voice_assistant                        # 3
        context.delegate = voice_assistant

        health_check(context.pattern_parser, manager.commands)              # 4

        main_task_group.soonify(speech_recognizer.start_listening)()        # 5
        microphone = Microphone(speech_recognizer.microphone_did_receive_sample)
        main_task_group.soonify(microphone.start_listening)()
        main_task_group.soonify(context.handle_responses)()

        detector = BlockageDetector()                                       # 6
        main_task_group.soonify(detector.monitor)()
```

1. `CommandsContext` is the engine, it holds the command manager, the processor pipeline (here, just pattern matching via `SearchProcessor`), and the task group everything else runs in.
2. `VoiceAssistant` is the default IO layer, gluing the recognizer and synthesizer to the context. See [Custom IO & Context Delegate](custom-interfaces.md) if you want to swap this out for something other than voice.
3. The recognizer and the context both report to `voice_assistant` as their delegate, this is the wiring that makes "the mic heard something" eventually become "a response got spoken."
4. `health_check` validates the whole command set at startup, catches things like a missing `@key` localization reference (see [Localizing Parsing](../localization-and-multilingual/localizing-parsing.md)) before a user ever triggers it.
5. Three tasks run concurrently for the lifetime of the assistant: listening for speech, reading microphone samples, and delivering queued responses. See [Sync vs Async Commands](../sync-vs-async-commands.md) for why this concurrency matters.
6. `BlockageDetector` watches the main thread and warns if something blocks it for too long, a safety net for the mistake [Optimization](optimization.md) is mostly about avoiding.

## Customizing the Run Function

Common reasons to write your own version instead of relying on [`run()`'s exposed parameters](../how-to-run.md):

- Extra concurrent tasks alongside the assistant (a background sync job, a health-check server, a metrics reporter)
- Custom logging or analytics wired in at the assembly point, not inside individual commands
- A different processor pipeline assembled conditionally, beyond what passing `processors=[...]` to `run()` already covers

When customizing, keep the core structure intact, task group creation, delegate wiring, and the order things are assigned in. Getting delegates assigned before tasks start matters; assign them too late and early events get dropped.

A "Hello, Stark!" assistant with a custom run, extending the default with one extra background task:

```python
import asyncer
import anyio
from stark import CommandsContext, CommandsManager, Response
from stark.core.health_check import health_check
from stark.core.processors.search_processor import SearchProcessor
from stark.general.blockage_detector import BlockageDetector
from stark.interfaces.microphone import Microphone
from stark.interfaces.protocols import SpeechRecognizer, SpeechSynthesizer
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.interfaces.silero import SileroSpeechSynthesizer
from stark.voice_assistant import VoiceAssistant


VOSK_MODEL_URL = "YOUR_CHOSEN_VOSK_MODEL_URL"
SILERO_MODEL_URL = "YOUR_CHOSEN_SILERO_MODEL_URL"

manager = CommandsManager()

@manager.new('hello')
async def hello_command() -> Response:
    return Response('Hello, Stark!')

async def periodic_health_ping():
    while True:
        await anyio.sleep(60)
        print('Still alive.')  # your monitoring/metrics call goes here

async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer,
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group=main_task_group,
            commands_manager=manager,
            processors=[SearchProcessor()],
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer=speech_recognizer,
            speech_synthesizer=speech_synthesizer,
            commands_context=context,
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant

        health_check(context.pattern_parser, manager.commands)

        main_task_group.soonify(speech_recognizer.start_listening)()
        microphone = Microphone(speech_recognizer.microphone_did_receive_sample)
        main_task_group.soonify(microphone.start_listening)()
        main_task_group.soonify(context.handle_responses)()
        main_task_group.soonify(periodic_health_ping)()  # the addition

        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()

async def main():
    recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)
    synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL)
    await run(manager, recognizer, synthesizer)

if __name__ == '__main__':
    anyio.run(main)
```

The only addition over the default is `periodic_health_ping`, everything else is the structure `run()` already does, copied so it can be extended in place.
