# Default Speech Interfaces

The Stark framework offers a default mechanism to incorporate speech interfaces from various platforms. This page elucidates the structure and usage of these interfaces.

## Overview

Stark's speech interfaces comprise two primary components:

1. **Speech Recognizers**: Convert spoken words into text.
2. **Speech Synthesizers**: Translate text into audible speech.

Both components employ protocols, ensuring flexibility and extensibility when opting for different implementations.

### VoskSpeechRecognizer

An implementation utilizing the Vosk library. This recognizer captures audio input and processes it via the Vosk offline speech recognition engine.

```python
def __init__(self, model_url: str):
```

### SileroSpeechSynthesizer

Implemented using Silero models. The resultant speech can be audibly played using the `Speech` class's `play()` method.

```python
def __init__(self, model_url: str, speaker: str = 'baya', threads: int = 4, device ='cpu', torch_backends_quantized_engine: str = 'qnnpack'):
```

### GCloudSpeechSynthesizer

This synthesizer leverages Google Cloud's Text-to-Speech service. Ensure your credentials are properly configured before usage. The synthesized speech can be stored as a file for subsequent playback.

```python
def __init__(self, voice_name: str, language_code: str, json_key_path: str):
```

## Usage

To integrate the speech interfaces:

1. Instantiate `CommandsManager`.
2. Select and instantiate your preferred speech recognizer.
3. Select and instantiate your preferred speech synthesizer.
4. Deploy the `run()` function, supplying it with the `CommandsManager`, recognizer, and synthesizer instances.

### Example

```python
manager = CommandsManager(...)
recognizer = VoskSpeechRecognizer(model_url="...")
synthesizer = SileroSpeechSynthesizer(model_url="...")

await run(manager, recognizer, synthesizer)
```

With the above configuration, your application will commence voice command listening and generate synthesized speech based on the logic within the commands manager.

## Notes

1. Confirm the required dependencies, such as Vosk, Silero, and Google Cloud, are in place (refer to [Installation](installation.md)).
2. Adequate error management and model verifications are essential for a production environment.
3. For more nuanced interactions based on speech recognition outcomes, adjust the delegates.

Harness Stark's default speech interfaces to effortlessly and flexibly craft voice-centric applications. Choose the most suitable recognizer and synthesizer for your requirements, and integrate them smoothly.

## Implementing Custom Speech Interface

For more information, consult [Custom Speech Interfaces](advanced/custom-speech-interfaces.md) under the "Advanced" section.
