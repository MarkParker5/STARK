# External Triggers

With the adaptability of Stark, VA can be integrated with various external triggers to provide a flexible and dynamic user experience. In the STARK framework, the integration of external triggers is seamless and can greatly enhance the interactivity of the assistant.

In this guide, we will walk through how to set up and use external triggers to activate the STARK Voice Assistant.

## Setting Up External Mode

The STARK framework provides a dedicated mode for external triggers: the "External" mode. When you set the VA mode to "external", it waits for an explicit trigger to activate the `SpeechRecognizer` component.

Additionally, you can utilize the `stop_after_interaction` property in custom modes:

```python
stop_after_interaction=True
```

When set to `True`, this ensures that after the VA finishes its current interaction, it stops the `SpeechRecognizer`, allowing for the next interaction to be initiated by an external trigger.

Details on the [Voice Assistant](https://stark.markparker.me/voice-assistant/index.md) page.

## Triggering Using `start_listening()`

Once the VA has stopped listening after an interaction, you can restart the `SpeechRecognizer` using the `start_listening()` method. This method serves as an entry point when you want to reactivate voice recognition after an external trigger.

## Implementing External Triggers

Do note that you probably need to implement a [custom run function](https://stark.markparker.me/advanced/custom-run/index.md) to add cuncurrent process or create a separate thread. If your trigger source isn't voice at all (a button, a webhook, a message), you likely want a custom [`CommandsContextDelegate`](https://stark.markparker.me/advanced/custom-interfaces/index.md) instead of `VoiceAssistant` entirely.

The beauty of external triggers lies in their versatility. Here are some ways to integrate them:

### Keyboard Hotkey Shortcut

A simple approach is to have a specific keyboard combination to activate Stark. Tools like Python's `keyboard` library can help in detecting specific keypresses, enabling you to then call `start_listening()`.

### Hardware Integration

For those looking for a hands-free approach, integrating hardware can be a fascinating option. For instance, using an Arduino microphone module, you can set up a system where Stark activates upon a distinct sound pattern, like a double or triple clap.

### Fast Wakeword Detectors

Wakeword detection is a popular approach in modern VAs. Using fast lightweight wakeword detectors like Picovoice's Porcupine, you can have your VA spring into action upon hearing a specific keyword or phrase.

### Implementations and Examples

You can find external trigger implementations at [stark_place/triggers](https://github.com/MarkParker5/STARK-PLACE/tree/master/stark_place/triggers) and examples of usage at [stark_place/examples](https://github.com/MarkParker5/STARK-PLACE/tree/master/stark_place/examples).

______________________________________________________________________

By embracing external triggers, you can elevate the adaptability and user experience of your voice assistant. Whether it's a simple keyboard shortcut or an intricate hardware setup, STARK's flexibility ensures that your VA is always ready and responsive, aligned with the needs of your user base.

Built a trigger that isn't listed here? A hardware sensor, a wakeword model, anything. Help is wanted expanding this list and the [stark_place/triggers](https://github.com/MarkParker5/STARK-PLACE/tree/master/stark_place/triggers) collection. [Discuss it](https://github.com/MarkParker5/STARK/discussions) before or after building, either works, and we need all the feedback we can get.
