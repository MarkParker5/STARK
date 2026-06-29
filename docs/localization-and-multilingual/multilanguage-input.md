# Multilanguage Input

When building custom IO interfaces (beyond the built-in Voice Assistant), you can provide per-word language metadata to the parsing pipeline via `TranscriptionString`. This metadata is optional — the parser works with plain strings and `LocaleString` too — but when available, it enables per-parameter language resolution for mixed-language input.

## TranscriptionString

`TranscriptionString` extends `LocaleString` with per-word language annotations:

```python
from stark.models.transcription_string import TranscriptionString

ts = TranscriptionString.from_words([
    ("set", "en"), ("timer", "en"), ("for", "en"),
    ("zwei", "de"), ("часа", "ru"),
])
# ts == "set timer for zwei часа"
# ts.language_code == "en" (majority language)
```

When the parser slices a parameter substring (e.g., `"zwei часа"` for a Duration parameter), `TranscriptionString` automatically resolves the majority language of that span — in this case `"de"`, not `"en"`. The parser then uses the German Duration pattern for matching and passes the correct language to `did_parse`.

All string operations (slicing, replace, strip, split) preserve the per-word language metadata.

## When to Use

Use `TranscriptionString` when your input source provides per-word language information:

- **STT engines** that tag each word with its detected language
- **NLP pipelines** that perform language identification per token
- **Translation APIs** that return source language annotations
- **Manual annotation** for testing multilingual commands

For single-language input, plain `LocaleString` is sufficient.

## Alternative Tracks

`TranscriptionString` can carry `alternative_texts` — the same utterance as processed by different language models:

```python
from stark.general.localisation import LocaleString

ts = TranscriptionString.from_words(
    [("set", "en"), ("timer", "en")],
    alternative_texts={
        "ru": LocaleString("сет таймер", "ru"),
        "de": LocaleString("set timer", "de"),
    },
)
```

When `STARK_ENABLE_MULTILANG_MATRIX=1` (default), the parser tries each alternative track against its language's command patterns concurrently, merging results. This catches commands that exist only in specific languages.

## VoiceTranscriptionString

For voice input, `VoiceTranscriptionString` extends `TranscriptionString` with time-aligned audio metadata:

```python
from stark.models.voice_transcription_string import VoiceTranscriptionString
```

This adds per-word timestamps, confidence scores, and speaker embeddings. This data is used by the parser to resolve overlapping matches across alternative tracks, set priorities, improve recognition accuracy. Speaker identification is not used yet, but this is something to be added in the future.

See [Voice Assistant](../voice-assistant.md) for the built-in multi-STT setup that produces `VoiceTranscriptionString` automatically.

## Passing to the Parser

Pass `TranscriptionString` (or any `LocaleString` subclass) directly to `process_string`:

```python
await context.process_string(ts)
```

The parser handles it as a regular string — `TranscriptionString` is a `str` subclass. The metadata enhances pattern resolution without requiring any changes to your commands or types.

See [Feature Flags](../advanced/feature-flags.md) for additional configuration options like tweaking multilingual features.
