# Speech Interface Protocols and Custom Implementation

When working with voice-driven applications, a robust and flexible architecture for handling both speech recognition and synthesis is vital. The Stark framework provides these features via interfaces (protocols) that can be easily extended and customized. This page dives deeper into the Stark framework's speech interface protocols and provides details on their implementation.

## Recognizer

### Protocol

```python
@runtime_checkable
class SpeechRecognizerDelegate(Protocol):
    async def speech_recognizer_did_receive_final_transcription(self, result: str): pass
    async def speech_recognizer_did_receive_partial_result(self, result: str): pass
    async def speech_recognizer_did_receive_empty_result(self): pass

@runtime_checkable
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    delegate: SpeechRecognizerDelegate | None
    
    async def start_listening(self): pass
    def stop_listening(self): pass
```

### Explanation

#### SpeechRecognizerDelegate

This protocol provides callback methods to output results of various states of the speech recognition:

- `speech_recognizer_did_receive_final_transcription`: Triggered when a final transcript is available.
- `speech_recognizer_did_receive_partial_result`: Fired upon receiving an interim transcript.
- `speech_recognizer_did_receive_empty_result`: Called when no speech was detected.

#### SpeechRecognizer

This protocol defines the primary input interface for any speech recognition implementation. It consists of:

- `is_recognizing`: A flag indicating if the recognizer is currently active.
- `delegate`: An instance responsible for handling the recognition results.
- `start_listening`: A method to initiate the listening process.
- `stop_listening`: A method to halt the listening process.

### Implementation Reference

To illustrate a custom implementation, we can reference the `VoskSpeechRecognizer`. This implementation leverages the Vosk offline speech recognition library. It downloads and initializes the Vosk model, sets up an audio queue, and provides methods to start and stop the recognition process.

For a deeper understanding, review the source code of the `VoskSpeechRecognizer` implementation.

<script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2FMarkParker5%2FSTARK%2Fblob%2Fmaster%2Fstark%2Finterfaces%2Fvosk.py&style=atom-one-dark&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"/></script>

## Synthesizer

### Protocol

```python
@runtime_checkable
class SpeechSynthesizerResult(Protocol):
    async def play(self): pass

@runtime_checkable   
class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str) -> SpeechSynthesizerResult: pass
```

### Explanation

- **SpeechSynthesizerResult**: This protocol defines a structure for the output of the speech synthesis process. It provides a method, `play`, to audibly present the synthesized speech.

- **SpeechSynthesizer**: This protocol represents the primary interface for any speech synthesis implementation. It contains:
  - `synthesize`: An asynchronous method that takes text input and returns a `SpeechSynthesizerResult` instance.

### Implementation Reference

For a hands-on example, the `SileroSpeechSynthesizer` and `GCloudSpeechSynthesizer` classes illustrate how one might implement the synthesizer protocol using the Silero models and Google Cloud Text-to-Speech services, respectively.

To gain more insights, you can check the source code of the `SileroSpeechSynthesizer` implementation.

<script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2FMarkParker5%2FSTARK%2Fblob%2Fmaster%2Fstark%2Finterfaces%2Fsilero.py&style=atom-one-dark&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>

## Alternative Interfaces

### CLI Interface

In this approach, you leverage the terminal or command line of a computer as the interface for both speech recognition and synthesis. Instead of speaking into a microphone and receiving audio feedback:

- **Recognition**: Users type their queries or commands into the terminal. The system then processes these textual inputs as if they were transcribed from spoken words.

- **Synthesis**: Instead of "speaking" or playing synthesized voice, the system displays the response as text in the terminal. This creates a chat-like experience directly within the terminal.

This is an excellent method for debugging, quick testing, or when dealing with environments where audio interfaces aren't feasible.

### GUI Interface

The GUI (Graphical User Interface) provides an intuitive and interactive way to implement custom speech interfaces for voice assistants. It offers a multifaceted experience, allowing users to:

- **Text Outputs**: Display text-based responses, enabling clear communication with users through written messages.

- **Context Visualization**: Visualize context and relevant information using graphics, charts, or interactive elements to enhance user understanding.

- **Text and Speech Input**: Accept input through both text and speech, allowing users to interact in the manner most convenient for them.

- **Trigger with Buttons**: Incorporate buttons or interactive elements that users can click or tap to initiate voice assistant interactions, providing a user-friendly interface.

The GUI interface serves as a versatile canvas for crafting engaging voice assistant experiences, making it an excellent choice for applications where graphical interaction enhances user engagement and comprehension.

### Telegram Bot as an Interface

Telegram, a popular messaging platform, provides an amazing bot API that developers can use to create custom bots. By leveraging this API, you can emulate speech interfaces in two distinct ways:

#### 1. **Voice Messages**

- **Recognition**: Users send voice messages to the Telegram bot. These voice messages can be transcribed into text using a speech recognition system. The recognized text can then be processed further by the bot for commands or queries.

- **Synthesis**: Instead of sending back text responses, the bot can use a text-to-speech system to generate voice messages, which it then sends back to the users. This method provides a more authentic "voice assistant" experience within the messaging environment.

By utilizing voice messages, you can create a more immersive experience for users, closely resembling interactions with traditional voice assistants.

#### 2. **Text Messages**

- **Recognition**: Users send text messages to the Telegram bot. The bot then treats these messages as if they were the transcribed text of spoken words.

- **Synthesis**: Rather than synthesizing spoken responses, the bot sends back text messages as its replies. The users read these messages as if they were listening to the synthesized voice of the system.

This approach offers a chat-like experience directly within the Telegram app, providing a seamless interaction that many users find intuitive.

In both methods, the use of a Telegram bot allows developers to introduce voice command functionalities in messaging environments, reaching users on various devices and platforms.

---

Venture in mind that these are mere illustrations of potential implementations. The canvas of possibilities is vast, bounded solely by the horizons of your creativity.
