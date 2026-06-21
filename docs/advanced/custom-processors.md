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

## Metadata Preservation

Input strings may carry metadata via `LocaleString` subclasses (`TranscriptionString`, `VoiceTranscriptionString`). This metadata includes per-word language codes, alternative transcription tracks, and voice timing data.

**Processors must never strip this metadata.** When transforming or slicing the input string, use the string's own methods (`_with`, `replace`, slicing) which preserve metadata through the `LocaleString` subclass chain. Avoid constructing plain `str` objects from metadata-carrying strings.

```python
# Good — preserves metadata:
modified = string.replace("old", "new")
substring = string[start:end]

# Bad — strips metadata:
modified = str(string).replace("old", "new")  # plain str, metadata lost
```

If a processor needs to pass additional context downstream, use `RecognizedEntity` objects — they're designed for inter-processor communication.
