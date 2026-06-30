# Roadmap

What's planned, in progress, or wanted next. This isn't a committed timeline, it's where to look if you want to know what's coming, or want to help build it.

## AI Agent Platform

The big one: an optional layer for building agents on top of S.T.A.R.K.'s existing background commands and LLM integration. See [AI Agent Platform](agent-platform.md) for the full plan.

## More Native Parsed Types

S.T.A.R.K. ships a small set of native types out of the box (`String`, `Word`, see [Patterns](patterns.md#native-types-list)) plus the ability to define your own `Object` types. More native types are actively being added, numbers, dates, durations, and similar commonly-needed parameter types, reducing how often you need to write a custom `Object` for something basic. **Status: work in progress.**

## More Interface Implementations & Platform Ports

S.T.A.R.K.'s protocols (`SpeechRecognizer`, `SpeechSynthesizer`, `CommandsContextDelegate`) are designed for exactly this, more backends and more ports are wanted, not just possible:

- More STT/TTS backends, see [Speech Recognition](tools/speech-recognition.md) and [Speech Synthesis](tools/speech-synthesis.md) for the protocols to implement against
- GUI and API interfaces, neither exists yet; see [How to Run, IO Options at a Glance](how-to-run.md#io-options-at-a-glance) and [Custom IO & Context Delegate](advanced/custom-interfaces.md)
- Porting to more platforms (mobile, embedded, browser)

**Status: help wanted.** If any of this sounds interesting, it's some of the highest-leverage contribution territory in the project, see [Project Ideas](project-ideas.md) and [STARK-PLACE](contributing-and-shared-usage-stark-place.md), or just open a [Discussion](https://github.com/MarkParker5/STARK/discussions) to talk through an approach before diving in.
