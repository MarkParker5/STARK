# Recognizable Alternatives (Fuzzy Command Matching)

> **Experimental.** This feature is functional but the API and behavior may change. See also [Phonetic Dictionary](phonetic-dictionary.md) which solves a similar problem at a different level. We're still exploring the best approach — feel free to use both, and please report your experience at https://github.com/MarkParker5/STARK/discussions.

Recognizable Alternatives is a fuzzy matching feature that widens command pattern regexes to accept phonetic variants of recognizable strings. When STT or user input contains a misspelling or phonetic approximation of a known keyword, this feature injects the variant into the compiled regex so the command still matches.

Example: user says "tern on the lite" → recognizable strings contain "turn" and "light" → regex expands `"turn"` to `"(turn|tern)"` and `"light"` to `"(light|lite)"` → command "turn on the light" matches.

## How It Works

The feature has two parts:

### 1. Generation: `RecognizableAlternativesProcessor`

A pipeline pre-processor that runs **before** `SearchProcessor`. For each recognizable string in the active language's `.strings` bundle, it slides a window over the input words and computes levenshtein similarity. Matches above 0.6 threshold are appended to `string.recognizable_alternatives`.

```python
from stark.core.processors import RecognizableAlternativesProcessor, SearchProcessor

context = CommandsContext(
    ...,
    processors=[
        RecognizableAlternativesProcessor(),  # generates alternatives
        SearchProcessor(),                     # uses them for matching
    ],
)
```

The processor only works on `TranscriptionString` inputs (which carry mutable `recognizable_alternatives`). Plain `str` or `LocaleString` inputs are passed through unchanged.

**Complexity:** O(R × W) levenshtein comparisons, where R = recognizable strings in the active language, W = words in input. Each comparison is O(len(candidate) × len(keyword)).

### 2. Expansion (automatic)

When `recognizable_alternatives` are present on the input string, `PatternParser.match()` automatically injects them into the compiled regex before `re.finditer`. For each `Suggestion(variant, keyword)`, if `keyword` appears as a literal in the compiled regex, it's replaced with `(keyword|variant1|variant2|...)`.

No flag needed — expansion is triggered by the presence of alternatives, which are only generated when `RecognizableAlternativesProcessor` is in the pipeline.

**Complexity:** O(S) string replacements per match attempt, where S = number of suggestions.

## Data Source

Alternatives are generated from the Localizer's **recognizable** `.strings` bundles — the same files used for `@key` pattern syntax. Each key-value pair is a keyword that the processor compares against the input:

```strings
/* strings/en/recognizable.strings */
"turn" = "turn";
"light" = "light";
"timer" = "timer";
```

## Comparison with NLDictionaryName

Both features do fuzzy matching, but at different levels and for different purposes:

| | Recognizable Alternatives | NLDictionaryName |
|---|---|---|
| **Best for** | Fuzzy command keyword matching | Fuzzy named entity parsing |
| **Level** | Pattern matching (before parsing) | Parameter parsing (inside `did_parse`) |
| **What it does** | Expands regex: `"hello"` → `"(hello\|helo)"` | Searches phonetic dictionary: `"parish"` → finds "Paris" |
| **Scope** | Static parts of all command patterns | Specific parameter types |
| **Data source** | Localizer `.strings` bundles | `Dictionary` with storage backend |
| **Complexity** | O(R × W) + O(S) | O(D) per candidate (mode-dependent) |

Use Recognizable Alternatives when command keywords are misheard. Use NLDictionaryName when parameter values (names, places, songs) need fuzzy matching against a large dataset. They can be used together — alternatives help the command match, NLDictionaryName helps the parameter parse.

See [Phonetic Dictionary](phonetic-dictionary.md) for NLDictionaryName details, [Custom Processors](../advanced/custom-processors.md) for pipeline setup, and [Feature Flags](../advanced/feature-flags.md) for configuration.
