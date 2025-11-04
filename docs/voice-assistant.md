# Voice Assistant (VA) Documentation

## Env Parameters

`STARK_VOICE_CLI`: Prints voice input and output in terminal if set to 1 (default 0). Useful for testing and debugging if no other interface is available.

## Overview

The VA processes user speech inputs, interacts with a set of commands, and provides responses. The behavior and response of the VA can be modified by setting different "modes". These modes define how the VA should operate in various situations, such as active listening, waiting, or when it's inactive.

## How the VA Works

### Responses and Contexts in Different Modes

The VA processes user inputs and responds based on the current context and mode. A context can be thought of as a state or situation in which the VA finds itself. Depending on the mode, the VA might immediately play responses, collect them for later, require explicit triggers to respond, or have different timeouts after which it changes its behavior or mode.

### Effects of Modes on VA

The mode can change the VA's behavior in various ways, such as:

- Whether to immediately play responses.
- Whether to collect responses for future playbacks.
- Setting a pattern for explicit interactions.
- Setting timeouts for interactions or before repeating a response.
- Switching to another mode either after a timeout or an interaction.
- Deciding to stop after an interaction.

## Mode Details

The `Mode` class defines the behavior and settings of the VA in various situations. Each property of the `Mode` class influences the VA's interaction with the user and the context.

### Mode Properties

- **`play_responses: bool` (default: `True`)**

   Determines whether the VA should immediately play the responses to user inputs. If set to `False`, the VA might hold onto responses for later or not vocalize them at all, based on other mode settings.

- **`collect_responses: bool` (default: `False`)**

   Indicates if the VA should collect responses for later playback. When set to `True`, responses might be saved and played back later, especially if `play_responses` is set to `False`.

- **`explicit_interaction_pattern: Optional[str]` (default: `None`)**

   This can be set to a specific string pattern. When defined, the VA requires an explicit interaction matching this pattern before processing user input. This is useful for "wake word" or command activation scenarios.

- **`timeout_after_interaction: int` (default: `20`)**

   Defines the number of seconds the VA waits after the last interaction before considering the session as timed out. Depending on other mode settings, the VA might change its behavior or switch modes after a timeout.

- **`timeout_before_repeat: int` (default: `5`)**

   Specifies the number of seconds before the VA can repeat a previously played response.

- **`mode_on_timeout: Callable[[], Mode] | None` (default: `None`)**

   Defines a function that returns another mode that the VA should switch to after a timeout.

- **`mode_on_interaction: Callable[[], Mode] | None` (default: `None`)**

   Determines a function that returns another mode that the VA should switch to upon receiving an interaction from the user.

- **`stop_after_interaction: bool` (default: `False`)**

   If set to `True`, the VA will stop its current operation after the command response. This is useful for situations where you want to start the VA on extarnal triggers, like keyboard shortcut.

### Native Modes

- **Active**: The VA is in an active listening state, transitioning to the "waiting" mode upon timeout.
- **Waiting**: The VA collects responses and goes back to the "active" mode upon user interaction.
- **Inactive**: The VA doesn't immediately play responses but collects them, reverting to "active" mode upon interaction.
- **Sleeping**: Similar to inactive, but requires an explicit interaction pattern to activate.
- **Explicit**: Requires a specific interaction pattern to proceed every command.
- **External**: Similar to Explicit, but requires an external trigger to activate.

### Mode Class Code

```python
class Mode(BaseModel):

    play_responses: bool = True
    collect_responses: bool = False
    explicit_interaction_pattern: Optional[str] = None
    timeout_after_interaction: int = 20 # seconds
    timeout_before_repeat: int = 5 # seconds
    mode_on_timeout: Callable[[], Mode] | None = None
    mode_on_interaction: Callable[[], Mode] | None = None
    stop_after_interaction: bool = False

    @classproperty
    def active(cls) -> Mode:
        return Mode(
            mode_on_timeout = lambda: Mode.waiting,
        )

    @classproperty
    def waiting(cls) -> Mode:
        return Mode(
            collect_responses = True,
            mode_on_interaction = lambda: Mode.active,
        )

    @classproperty
    def inactive(cls) -> Mode:
        return Mode(
            play_responses = False,
            collect_responses = True,
            timeout_after_interaction = 0, # start collecting responses immediately
            timeout_before_repeat = 0, # repeat all
            mode_on_interaction = lambda: Mode.active,
        )

    @classmethod
    def sleeping(cls, pattern: str) -> Mode:
        return Mode(
            play_responses = False,
            collect_responses = True,
            timeout_after_interaction = 0, # start collecting responses immediately
            timeout_before_repeat = 0, # repeat all
            explicit_interaction_pattern = pattern,
            mode_on_interaction = lambda: Mode.active,
        )

    @classmethod
    def explicit(cls, pattern: str) -> Mode:
        return Mode(
            explicit_interaction_pattern = pattern,
        )

    @classmethod
    def external(cls) -> Mode:
        return Mode(
            stop_after_interaction = True,
        )
```

## Changing Modes Manually

You can manually set the mode by assigning a Mode object to the VA's `mode` attribute. For instance, to set the VA to "waiting" mode:

```python
voice_assistant.mode = Mode.waiting
```

## Setting Up a Custom Mode

To define a custom mode, create an instance of the `Mode` class and specify the desired properties. For example:

```python
custom_mode = Mode(play_responses=False, timeout_after_interaction=10)
voice_assistant.mode = custom_mode
```

## Setting VA Modes from Command

To have commands in the VA interact with its modes.

1. Register VA in DIContainer

2. Add VA as a command dependency

3. Access VA in command

*check [Dependency Injection](dependency-injection.md) for details*

## Customizing VA and Observing Events

If you want to add a custom logic to VA events, for example update GUI, you can subclass the native VoiceAssistant class and override its methods to add desired behavior. Don't forget to call the superclass method to ensure the default behavior is preserved. Voice assistant conforms to SpeechRecognizerDelegate and CommandsContextDelegate protocols, which methods are the main events.

```python
class MyVoiceAssistant(VoiceAssistant):

    async def speech_recognizer_did_receive_final_result(self, result: str):
        super().speech_recognizer_did_receive_final_result(result)
        print('You sad: ', result) # Your custom logic here

    async def speech_recognizer_did_receive_partial_result(self, result: str):
        super().speech_recognizer_did_receive_partial_result(result)
        print(f"\rListening...: \x1b[3m{result}\x1b[0m", end="") # Your custom logic here

    async def speech_recognizer_did_receive_empty_result(self):
        super().speech_recognizer_did_receive_empty_result()
        # Your custom logic here

    async def commands_context_did_receive_response(self, response: Response):
        super().commands_context_did_receive_response(response)
        print('STARK: ', response.text) # Your custom logic here
```

For more advanced usage, see the source code or use your IDE's autocomplete. Most modern editors support "go to definition" feature which might be very helpful for this.
