# Custom Processors

Processors form a modular pipeline for string pre-processing and command search. Each processor in the pipeline receives the input string and can either find commands, enrich the parsing context, or pass through to the next processor.

## Pipeline Architecture

When `CommandsContext.process_string()` is called, it runs the input through each processor in order:

1. Each processor receives the input string and the current context
2. If a processor returns non-empty results, processing stops
3. If all processors return empty, the context resets to root

This enables multistage processing: NER pre-processors mark entities, then the search processor matches commands using that enriched context, and in the end there are fallback processors that handle unmatched input, for example, passing the request to a search engine, external API, or an AI model.

## Built-in Processors

- **`SearchProcessor`** — the default command search. Matches input against all registered command patterns using `PatternParser.match()`. Handles overlap resolution and matrix cross-language matching.
- **`SpacyNERProcessor`** — pre-processor that uses spaCy to mark named entities (locations, organizations, etc.) as `RecognizedEntity` objects. These are passed to subsequent processors to improve parameter extraction.

## Creating a Custom Processor

Subclass `CommandsContextProcessor` and override either `process_string` (for pipeline-wide logic) or `process_context_layer` (for per-context-layer logic):

```python
from stark.core.commands_context_processor import CommandsContextProcessor

class MyPreProcessor(CommandsContextProcessor):
    async def process_string(self, string, context, recognized_entities):
        # Pre-process: add recognized entities, transform string, etc.
        # Return ([], 0) to pass through to the next processor
        return [], 0

class MySearchProcessor(CommandsContextProcessor):
    async def process_context_layer(self, string, context, context_layer, recognized_entities):
        # Search for commands in this context layer
        # Return list of SearchResult
        return []
```

## Registering Processors

Pass your processors to `CommandsContext` or `run()`:

```python
context = CommandsContext(
    task_group=main_task_group,
    commands_manager=manager,
    processors=[MyPreProcessor(), SearchProcessor()],
)
```

Order matters — pre-processors should come before search processors.

## Metadata on Input Strings

Input strings may carry metadata via `LocaleString` or subclasses (`TranscriptionString`, `VoiceTranscriptionString`). Processors can **read** this metadata:

- `string.language_code` — the majority language of the input
- `string.words` — per-word language annotations (if `TranscriptionString`)
- `string.suggestions` — phonetic suggestion variants (if populated by STT relay)
- `string.alternative_texts` — same utterance transcribed by different language models
- `string.track` — voice timing/confidence data (if `VoiceTranscriptionString`)

Processors **cannot mutate** the string's metadata — `LocaleString` subclasses are immutable (str subclass). To transform the string, use its methods (`replace`, slicing, `_with`) which return new instances with preserved metadata.

**Processors must never strip metadata.** Avoid constructing plain `str` objects from metadata-carrying strings:

```python
# Good — preserves metadata:
modified = string.replace("old", "new")
substring = string[start:end]

# Bad — strips metadata:
modified = str(string).replace("old", "new")  # plain str, metadata lost
```

## Inter-Processor Communication

### `RecognizedEntity`

A `RecognizedEntity` marks a substring that likely corresponds to a specific named entity or parameter type — it doesn't parse the substring, but narrows the search bounds for subsequent processors. This is valuable because finding the correct substring boundaries is the hardest part of parameter parsing.

```python
recognized_entities.append(RecognizedEntity(
    substring="London",
    type=Location,  # the Object type this substring likely matches
))
```

The `SearchProcessor` uses recognized entities to constrain parameter extraction — when a `RecognizedEntity` matches a parameter's type and its substring appears within the parameter's regex match, the parser narrows to that exact substring instead of the full regex capture.
