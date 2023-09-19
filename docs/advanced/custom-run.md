# Custom Run

STARK's flexibility and extensibility can be attributed to its ability to cater to various use cases and environments. An essential feature of the framework is the capacity to customize the run function. This allows developers to personalize the core functionality, integrating custom setups, or extending the capabilities of the framework.

Below is a quick guide on how to understand and make use of the custom run function.

## Understanding the Default Run Function

The `run` function in STARK serves as the primary entry point that sets up and commences the voice assistant.

```python
import asyncer

from stark.interfaces.protocols import SpeechRecognizer, SpeechSynthesizer
from stark.core import CommandsContext, CommandsManager
from stark.voice_assistant import VoiceAssistant
from stark.general.blockage_detector import BlockageDetector


async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer = speech_recognizer,
            speech_synthesizer = speech_synthesizer,
            commands_context = context
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant
        
        main_task_group.soonify(speech_recognizer.start_listening)()
        main_task_group.soonify(context.handle_responses)()
        
        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()

```

Let's dissect it:

```python
async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer
):

```

**Parameters:**

- `manager`: An instance of `CommandsManager` which holds all the commands that the voice assistant can recognize and process.
- `speech_recognizer`: The implementation you've selected for speech recognition.
- `speech_synthesizer`: The implementation you've chosen for speech synthesis.

```python
async with asyncer.create_task_group() as main_task_group:
```

Here, a task group is created using `asyncer`. Task groups allow you to manage several tasks concurrently.

```python
context = CommandsContext(
    task_group = main_task_group, 
    commands_manager = manager
)
```

A `CommandsContext` is initialized. This holds the context in which commands are executed, including the associated task group and the command manager.

```python
voice_assistant = VoiceAssistant(
    speech_recognizer = speech_recognizer,
    speech_synthesizer = speech_synthesizer,
    commands_context = context
)
```

The `VoiceAssistant` is then created and initialized with the recognizer, synthesizer, and context.

```python
speech_recognizer.delegate = voice_assistant
context.delegate = voice_assistant
```

Both the speech recognizer and the commands context are associated with the voice assistant as their delegates. This setup ensures that when the recognizer captures any speech or when there's a command response to handle, the voice assistant processes them.

```python
main_task_group.soonify(speech_recognizer.start_listening)()
main_task_group.soonify(context.handle_responses)()
```

Tasks are added to the main task group: One to start the speech recognizer's listening process, and the other to handle responses from executed commands.

```python
detector = BlockageDetector()
main_task_group.soonify(detector.monitor)()
```

A blockage detector is introduced and initialized. This mechanism ensures that any potential deadlocks or blocking calls within the async code are detected, allowing for smooth operation.

## Customizing the Run Function

Customizing the `run` function provides a pathway to inject additional functionalities or to adapt the framework to specific needs.

For instance, you could:

- Integrate other third-party tools or services.
- Implement custom logging or analytics mechanisms.
- Extend with other asynchronous operations to run concurrently with the voice assistant.

When customizing, ensure that you maintain the core structure, especially the initialization of the main components and the task group management. The ordering can be crucial, especially when setting delegates.

To kickstart your customization, replicate the default run function as your foundation, and weave in your specific adjustments or additions as needed. Consequently, a "Hello, World" implementation with a custom run would appear as:

```python
import asyncer
from stark import CommandsContext, CommandsManager, Response
from stark.interfaces.protocols import SpeechRecognizer, SpeechSynthesizer
from stark.interfaces import VoskSpeechRecognizer, SileroSpeechSynthesizer
from stark.voice_assistant import VoiceAssistant
from stark.general.blockage_detector import BlockageDetector


VOSK_MODEL_URL = "YOUR_CHOSEN_VOSK_MODEL_URL"
SILERO_MODEL_URL = "YOUR_CHOSEN_SILERO_MODEL_URL"

recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)
synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL)

manager = CommandsManager()

@manager.new('hello')
async def hello_command() -> Response:
    text = voice = 'Hello, world!'
    return Response(text=text, voice=voice)

async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer = speech_recognizer,
            speech_synthesizer = speech_synthesizer,
            commands_context = context
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant
        
        main_task_group.soonify(speech_recognizer.start_listening)()
        main_task_group.soonify(context.handle_responses)()
        
        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()

async def main():
    await run(manager, recognizer, synthesizer)

if __name__ == '__main__':
    asyncer.runnify(main)() # or anyio.run(main()), same thing
```
