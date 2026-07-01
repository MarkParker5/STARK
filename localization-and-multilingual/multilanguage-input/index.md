# Multilanguage Input

When building custom IO interfaces (beyond the built-in Voice Assistant), you can provide per-word language metadata to the parsing pipeline via `TranscriptionString`. This metadata is optional, the parser works with plain strings and `LocaleString` too, but when available, it enables per-parameter language resolution for mixed-language input.

## TranscriptionString

`TranscriptionString` extends `LocaleString` with per-word language annotations:

```python
from stark.models.transcription_string import TranscriptionString

# road trip across Europe
ts = TranscriptionString.from_words([
    ("navigate", "en"), ("from", "en"),
    ("Köln", "de"),
    ("to", "en"),
    ("Wrocław", "pl"),
    ("and", "en"), ("play", "en"),
    ("Zitti", "it"), ("e", "it"), ("Buoni", "it"),
])
# ts == "navigate from Köln to Wrocław and play Zitti e Buoni"
# ts.language_code == "en" (majority: 5 en words vs. 3 it, 1 de, 1 pl)
```

Per-word language metadata can come from an STT engine that identifies each word's language, for example when a bilingual speaker switches mid-sentence, or from a shared device in an office or household where different people speak different languages, or a command that genuinely spans languages (city names, product names, a number said in one language mid-sentence in another). The parser slices each span as its own parameter and resolves its language independently:

```python
ts[ts.index("Köln"):][:4]           # "Köln" → language_code "de"
ts[ts.index("Wrocław"):][:7]        # "Wrocław" → language_code "pl"
ts[ts.index("Zitti e Buoni"):]      # "Zitti e Buoni" song by Måneskin → language_code "it"
```

Each slice resolves the majority language of that span, not the sentence's overall `"en"`. That resolved language is what gets passed to `did_parse` for each parameter's type. See [Phonetic Dictionary](https://stark.markparker.me/tools/phonetic-dictionary/index.md) for matching names across languages and spellings.

All string operations (slicing, replace, strip, split) preserve the per-word language metadata.

## When to Use

Use `TranscriptionString` when your input source provides per-word language information:

- **STT engines** that tag each word with its detected language
- **NLP pipelines** that perform language identification per token
- **Translation APIs** that return source language annotations
- **Manual annotation** for testing multilingual commands

For single-language input, plain `LocaleString` is sufficient.

## Alternative Tracks

`TranscriptionString` can carry `alternative_texts`, the same utterance as processed by different language models:

```python
from stark.general.localisation import LocaleString

ts = TranscriptionString.from_words(
    [("set", "en"), ("timer", "en")],
    alternative_texts={
        "es": LocaleString("pon el temporizador", "es"),
        "de": LocaleString("set timer", "de"),
        "fr": LocaleString("mets le minuteur", "fr"),
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

See [Voice Assistant](https://stark.markparker.me/voice-assistant/index.md) for the built-in multi-STT setup that produces `VoiceTranscriptionString` automatically.

## Passing to the Parser

Pass `TranscriptionString` (or any `LocaleString` subclass) directly to `process_string`:

```python
await context.process_string(ts)
```

The parser handles it as a regular string, `TranscriptionString` is a `str` subclass. The metadata enhances pattern resolution without requiring any changes to your commands or types.

See [Feature Flags](https://stark.markparker.me/advanced/feature-flags/index.md) for additional configuration options like tweaking multilingual features.
