# First Steps

Congratulations on installing the STARK framework! This guide is designed to help you familiarize yourself with its primary components and to set up your first voice-driven application using STARK. We'll demonstrate how to create a basic voice assistant that responds to the "hello" command.

## Hello World

STARK provides flexibility by allowing you to integrate different implementations for speech recognition and synthesis. For this tutorial, we will employ the Vosk implementation for speech recognition and the Silero implementation for speech synthesis.

Before diving in, you'll need to specify URLs for the models. Both Vosk and Silero are designed to automatically download and cache the models upon their first use.

- [Vosk Model URL: Visit Vosk models to select an appropriate model.](https://alphacephei.com/vosk/models)
- [Silero Model URL: Visit Silero models to identify a suitable model.](https://github.com/snakers4/silero-models?tab=readme-ov-file#models-and-speakers)

At the heart of STARK is the `CommandsManager`, a component dedicated to managing the commands your voice assistant can comprehend. Here's a comprehensive example showcasing how to define a new command, initialize the speech recognizer and synthesizer, and run the voice assistant:

```py
import anyio
from stark import run, CommandsManager, Response
from stark.interfaces import VoskSpeechRecognizer, SileroSpeechSynthesizer


VOSK_MODEL_URL = "YOUR_CHOSEN_VOSK_MODEL_URL"
SILERO_MODEL_URL = "YOUR_CHOSEN_SILERO_MODEL_URL"

recognizer = VoskSpeechRecognizer(model_url=VOSK_MODEL_URL)
synthesizer = SileroSpeechSynthesizer(model_url=SILERO_MODEL_URL)

manager = CommandsManager()

@manager.new('hello')
async def hello_command() -> Response:
    text = voice = 'Hello, world!'
    return Response(text=text, voice=voice)

async def main():
    await run(manager, recognizer, synthesizer)

if __name__ == '__main__':
    anyio.run(main())
```

In this code snippet, we defined a new command for the voice assistant. When the word "hello" is spoken, the `hello_command` function is triggered, which then issues a greeting in response.

It's important to note that STARK accommodates both synchronous (`def`) and asynchronous (`async def`) command definitions. For a deeper dive into the use-cases and distinctions between these two command types, consult the [Sync vs Async Commands](sync-vs-async-commands.md) article.
