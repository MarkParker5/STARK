# Corrections (Pattern Extension for Phonetic Matching) \[EXPERIMENTAL]

Corrections is a matching feature that widens command pattern to accept translation/phonetic variants of known keywords. When STT or user input contains a misspelling or phonetic approximation, this feature injects the variant into the compiled pattern so the command still matches.

Example: user says "tern on the lite" → dictionary contains "turn" and "light" → regex expands `"turn"` to `"(turn|tern)"` and `"light"` to `"(light|lite)"` → command "turn on the light" matches.

## How It Works

The feature has three parts:

### 1. Generation: `CorrectionsProcessor`

A pipeline pre-processor that runs **before** `SearchProcessor`. It accepts one or more `Dictionary` instances and uses their phonetic matching infrastructure (IPA→simplephone→levenshtein with proximity graph) to find corrections.

```python
from stark.core.processors import CorrectionsProcessor, SearchProcessor
from stark.tools.dictionary import build_recognizable_dictionary
from stark.tools.phonetic.transcription import LatinPassthroughProvider

# Build a dictionary from recognizable.strings bundles
dictionary = build_recognizable_dictionary(localizer, ipa_provider=LatinPassthroughProvider())

context = CommandsContext(
    ...,
    processors=[
        CorrectionsProcessor(dictionaries=[dictionary]),  # generates corrections
        SearchProcessor(),                                 # uses them for matching
    ],
)
```

When a `localizer` is provided and no custom `processors` are specified, `CorrectionsProcessor` is included automatically in the default pipeline.

The processor accepts any `Dictionary` instance — not just ones built from recognizable.strings. You can pass custom dictionaries populated with domain-specific vocabulary.

**Lookup modes:** The processor supports the same modes as `Dictionary`: `EXACT`, `CONTAINS`, `FUZZY`, and `AUTO` (default). Pass via `CorrectionsProcessor(dictionaries=[...], mode=LookupMode.FUZZY)`. See [Phonetic Dictionary](phonetic-dictionary.md) for more details.

**Multilingual:** For `TranscriptionString` with alternative tracks, the processor runs dictionary search per each track and stores per-track corrections. See [Localization and Multilingual](../localization-and-multilingual/index.md)

### 2. Expansion (automatic)

When corrections are present on the input string, `PatternParser.match()` automatically injects them into the compiled pattern before matching. For each `Correction(variant, keyword)`, if `keyword` appears as a literal in the compiled regex, it's replaced with `(keyword|variant1|variant2|...)`.

No flag needed despite being an experimental feature — expansion is triggered by the presence of corrections.

### 3. Back-tracking

After a successful match, `MatchResult` records which corrections were applied:

- `corrections: dict[str, str]` — maps each variant to its keyword (e.g. `{"tern": "turn"}`)
- `corrected_string: str` — the matched substring with corrections applied (e.g. `"turn on the light"`)

This enables UIs to show the corrected text to the user, and simplifies debugging.

## Data Sources

### Recognizable Strings (built-in)

`build_recognizable_dictionary()` creates a Dictionary from all loaded `recognizable.strings` bundles. See [Localizing Parsing](../localization-and-multilingual/localizing-parsing.md)

### Custom Dictionaries

Any `Dictionary` instance works — populate it with domain-specific vocabulary:

```python
from stark.tools.dictionary import Dictionary
from stark.tools.dictionary.storage import DictionaryStorageMemory
from stark.tools.dictionary import build_recognizable_dictionary

recognizable_dict = build_recognizable_dictionary(localizer)

custom_dict = Dictionary(storage=DictionaryStorageMemory())
custom_dict.write_one("en", "spotify")
custom_dict.write_one("en", "bluetooth")

processor = CorrectionsProcessor(dictionaries=[recognizable_dict, custom_dict])
```

## IPA Provider Options

Dictionary-based matching uses IPA transcription for cross-language phonetic comparison. Available providers. 

```python
from stark.tools.phonetic.transcription import LatinPassthroughProvider, EspeakIpaProvider

dict = build_recognizable_dictionary(
    localizer,
    ipa_provider=LatinPassthroughProvider(fallback=EspeakIpaProvider()),
)
```

See [Phonetic Dictionary](phonetic-dictionary.md) and [Phonetic Tools](raw-phonetic.md) for more details and native implementations.

## Comparison with NLDictionaryName

Both features use `Dictionary` for phonetic matching, but at different levels:

| | Corrections | NLDictionaryName |
|---|---|---|
| **Best for** | Fuzzy command keyword matching | Fuzzy named entity parsing |
| **Level** | Pre-processor + Pattern matching (before parsing) | Parameter parsing (inside `did_parse`) |
| **What it does** | Expands patterns with homophones of known words found in the request string | Searches through dictionary programmatically if pattern matched |
| **Scope** | Scans the entire input string (pre-processing), affects all commands, only expands with homophones present in both the request string and the dictionary | Specific parameter types for commands matched by pattern |
| **Data source** | All provided `Dictionary` objects | Specific `Dictionary` |
| **Cross-language** | Yes | Yes |
| **Extra requirements** | keyword must be present in the compiled pattern as a literal | none, can have "**" pattern |
| **Overhead** | Longer pre-processing, fast matching | No pre-processing, longer matching |

Corrections are helpful for keywords that are present as literals and can be misheard. NLDictionaryName are designed for extraction of named-entity parameters (names, places, songs). They share the same `Dictionary` infrastructure as a backend, but apply it differently. Both are in experimental stages, please try both and provide feedback.

See [Phonetic Dictionary](phonetic-dictionary.md) for Dictionary and NLDictionaryName details, [Custom Processors](../advanced/custom-processors.md) for pipeline setup.
