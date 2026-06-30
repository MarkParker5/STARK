# Custom Processors

Processors form a modular pipeline for string pre-processing and command search. Each processor in the pipeline receives the input string and can either find commands, enrich the parsing context, or pass through to the next processor.

## Data Flow

```
process_string(input)
    │
    ▼
┌─────────────────────────────────────┐
│  Processor 1: Pre-processing        │  e.g. CorrectionsProcessor
│  Input: string, recognized_entities │  - reads string metadata
│  Output: ([], 0) — pass-through     │  - updates corrections
│  Side effects:                      │  - appends to recognized_entities
│    string.corrections               │
│    recognized_entities              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Processor 2: Pre-processing        │  e.g. SpacyNERProcessor
│  Input: string, recognized_entities │  - reads string text
│  Output: ([], 0) — pass-through     │  - appends RecognizedEntity objects
│  Side effects:                      │
│    recognized_entities              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Processor 3: Search                │  e.g. SearchProcessor
│  Input: string, recognized_entities │  - uses corrections
│  Output: ([SearchResult, ...], 0)   │    for pattern expansion
│  Uses:                              │  - uses recognized_entities
│    PatternParser.match()            │    for parameter extraction
│    string.translate_position()      │  - uses alternative_texts
│    string[start:end]                │    for matrix matching
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Processor 4: Fallback (optional)   │  e.g. LLM, web search,
│  Only reached if Processor 3        │  template response
│  returned no results                │
└─────────────────────────────────────┘
```

When `CommandsContext.process_string()` is called, it runs the input through each processor in order:

1. Each processor receives the **same** `string` object and the **shared** `recognized_entities` list
2. If a processor returns non-empty results, processing **stops**, subsequent processors are skipped
3. Pre-processors return `([], 0)` to pass through without stopping the pipeline
4. If all processors return empty, the context resets to root

## Built-in Processors

### `CorrectionsProcessor` (pre-processor)

Generates phonetic corrections using `Dictionary`-based phonetic matching. Accepts any `Dictionary` instances, including one built from recognizable.strings via `build_recognizable_dictionary()`. For each input word/phrase, runs dictionary sentence search and appends matching corrections to `string.corrections`.

These corrections are consumed by `PatternParser._expand_corrections()` to widen compiled patterns, e.g., `"hello"` in the compiled pattern becomes `"(hello|helo)"`.

Included automatically for recognizable.strings in the default pipeline when a `localizer` is provided.

See [Corrections](../tools/corrections.md) for full documentation.

### `SpacyNERProcessor` (pre-processor)

Uses spaCy NER to mark named entities (locations, organizations, etc.) as `RecognizedEntity` objects. These narrow parameter extraction bounds in subsequent processors.

**Complexity:** O(N) where N = input length (spaCy's neural model). Memory: proportional to model size.

### `SearchProcessor` (command search)

Matches input against all registered command patterns. Handles:
- Pattern matching via `PatternParser.match()`, O(C × P) where C = commands in the current context window, P = pattern complexity
- Matrix cross-language matching across alternative tracks (when `STARK_ENABLE_MULTILANG_MATRIX=1`), multiplies by T (number of tracks which is the number of languages with active STT)
- Corrections pattern expansion, O(C) string replacements per match, where C = corrections
- Overlap resolution with cross-track position translation, O(R), where R = results

**Complexity:** O(T × C × P) for matching + O(R) for overlap resolution

## Creating a Custom Processor

Subclass `CommandsContextProcessor` and override either `process_string` (for pipeline-wide logic) or `process_context_layer` (for per-context-layer logic):

```python
from stark.core.commands_context_processor import CommandsContextProcessor

class MyPreProcessor(CommandsContextProcessor):
    async def process_string(self, string, context, recognized_entities):
        # Pre-process: enrich metadata, add recognized entities
        # Return ([], 0) to pass through to the next processor
        return [], 0

class MySearchProcessor(CommandsContextProcessor):
    async def process_context_layer(self, string, context, context_layer, recognized_entities):
        # Search for commands in this context layer
        # Return list of SearchResult
        return []
```

## Registering Processors

Pass your processors to `CommandsContext` or `run()`. Order matters, pre-processors before search, search before fallback:

```python
from stark.core.processors import CorrectionsProcessor, SearchProcessor, SpacyNERProcessor
from stark.tools.dictionary import build_recognizable_dictionary

context = CommandsContext(
    task_group=main_task_group,
    commands_manager=manager,
    processors=[
        CorrectionsProcessor(dictionaries=[dictionary]),  # 1. generate phonetic corrections
        SpacyNERProcessor(lang_models={"en": "en_core_web_sm"}),  # 2. mark entities
        SearchProcessor(),  # 3. match commands
        # MyFallbackProcessor(),  # 4. optionally handle unmatched input
    ],
)
```

## Metadata on Input Strings

Input string may be a plain python str, but also may carry metadata via `LocaleString` or subclasses. Processors can read metadata and append to mutable fields. STARK provides next table of metadata attributes available on `LocaleString` subclasses:

| Attribute | Type | LocaleString Subclass | Description |
|-----------|------|--------|-------------|
| `language_code` | `LanguageCode` | All `LocaleString` | Majority language of the input |
| `words` | `tuple[TranscriptionWord]` | `TranscriptionString` | Per-word language annotations |
| `corrections` | `list[Correction]` | `TranscriptionString` | **Mutable.** Phonetic corrections for pattern expansion |
| `alternative_texts` | `dict[str, LocaleString]` | `TranscriptionString` | Same utterance from different language models |
| `track` | `VoiceTranscriptionTrack` | `VoiceTranscriptionString` | Word timestamps, confidence, speaker data. Subclass of `TranscriptionString`. Produced by `VoskSpeechRecognizer` and passed unchanged by `VoiceAssistant` |

The type of the input string is determined by the IO layer (like STARK's `VoiceAssistant`). You can implement your own IO and processor layers and pass any metadata by subclassing `LocaleString` or its subclasses.

## Inter-Processor Communication

### `RecognizedEntity`

Marks a substring that likely corresponds to a specific named entity or parameter type. It narrows parameter extraction bounds, the hardest part of parsing.

```python
recognized_entities.append(RecognizedEntity(
    substring="London",
    type=Location,
))
```

`SearchProcessor` uses these to constrain parameter extraction, when a `RecognizedEntity` matches a parameter's type and appears within the pattern match, the parser narrows to that exact substring.

### `corrections`

Phonetic correction variants on `TranscriptionString`. Pre-processors append `Correction(variant, keyword)` pairs. `SearchProcessor` injects these into compiled patterns.

```python
from stark.models.voice_transcription import Correction
string.corrections.append(
    Correction(variant="helo", keyword="hello")
)
```
