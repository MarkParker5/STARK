# Project Ideas

Looking for something to build with S.T.A.R.K.? Here are ideas grouped by what they're good for, each one is picked to exercise a specific feature, not just be another smart-home command (Archie's already got that covered, see [Powered By](https://stark.markparker.me/#powered-by-stark)).

## PC Control

- **Hotkey-triggered assistant**: wake the assistant with a keyboard shortcut instead of a wake word. Showcases [External Triggers](https://stark.markparker.me/advanced/external-triggers/index.md) and `Mode.external()`.
- **System control**: volume, brightness, launching apps, window management. Showcases [Patterns](https://stark.markparker.me/patterns/index.md) for matching varied phrasing ("turn it up" vs "volume to 80%").
- **Tray/statusbar companion**: runs quietly, shows status, triggers on click. Showcases a custom [`CommandsContextDelegate`](https://stark.markparker.me/advanced/custom-interfaces/index.md) instead of voice.

## Service Integrations

- **Media lookup**: query YouTube, Spotify, or IMDB and read back results. Showcases [Dependency Injection](https://stark.markparker.me/dependency-injection/index.md) for API clients and async commands for network calls.
- **"What's playing" + queue control**: start playback, then offer follow-ups (skip, pause, queue another). Showcases [Commands Context](https://stark.markparker.me/commands-context/index.md) for the follow-up menu.

## Background & Long-Running Tasks

- **Download/upload tracker**: start a transfer, get progress updates, optionally cancel mid-flight. Directly the [background commands](https://stark.markparker.me/sync-vs-async-commands/#background-commands) pattern, timer, but for files.
- **Reminder/notification assistant**: schedule something, get notified later regardless of what else you're doing. Showcases [Multiple Responses](https://stark.markparker.me/command-response/index.md) and [Voice Assistant Modes](https://stark.markparker.me/voice-assistant/index.md).

## Raspberry Pi & Hardware

- **Fully offline Pi assistant**: Vosk + Silero on a Pi, no cloud dependency. Showcases the "100% on-device" pillar end to end, see [Where to Host](https://stark.markparker.me/where-to-host/index.md).
- **Robotics voice control**: drive a robot, control a motor, trigger a routine by voice. Showcases [External Triggers](https://stark.markparker.me/advanced/external-triggers/index.md) for hardware integration (sensors, button presses) alongside voice.

## Voice UI & Games

- **Branching dialogue / text adventure**: each "room" or "scene" is a context, offering different commands depending on where the player is. The most natural fit for [Commands Context](https://stark.markparker.me/commands-context/index.md) outside of a literal menu, contexts as game state.
- **Quiz or trivia game**: multilingual questions, [Going Multilingual](https://stark.markparker.me/localization-and-multilingual/index.md) showcased as a feature, not just a setting.

## Porting & New Interfaces

- **GUI or Telegram bot interface**: neither exists yet in S.T.A.R.K.; see [How to Run](https://stark.markparker.me/how-to-run/#io-options-at-a-glance) and [Custom IO & Context Delegate](https://stark.markparker.me/advanced/custom-interfaces/index.md) for where to start. High-leverage: whatever you build, others can reuse.
- **New STT/TTS backend**: wrap a model or cloud API you like behind the existing protocols. See [Speech Recognition](https://stark.markparker.me/tools/speech-recognition/index.md) and [Speech Synthesis](https://stark.markparker.me/tools/speech-synthesis/index.md).

## More Ideas

Check [ideas thread in discussions](https://github.com/ai21labs/STARK/discussions/21) for more inspiration.

______________________________________________________________________

## Built Something? Tell Us

This list is here to spark ideas, not box you in. Whatever you actually build, even if it's half-finished, weird, or "probably not interesting to anyone else," [post it in Discussions](https://github.com/MarkParker5/STARK/discussions). We need all the feedback we can get to make S.T.A.R.K. better, so don't be afraid to be first; every thread starts with one post, and a small, honest write-up of what you tried is worth more than a polished announcement nobody made. If it's reusable by others, [contribute it to STARK-PLACE](https://stark.markparker.me/contributing-and-shared-usage-stark-place/index.md) too, but Discussions first is always fine.
