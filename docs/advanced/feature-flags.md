# Feature Flags

S.T.A.R.K uses environment variables to enable or disable experimental and optional features.

## Available Flags

| Flag | Default | Complexity overhead | Description |
|------|---------|-------------------|-------------|
| `STARK_ENABLE_VOICE_CLI` | `0` | None | Print voice input/output in terminal. See [Voice Assistant](../voice-assistant.md). |
| `STARK_ENABLE_MULTILANG_MATRIX` | `1` | O(T × C × P) — multiplies matching cost by T tracks | Match input against all alternative language tracks concurrently. See [Multilanguage Input](../localization-and-multi-language/multilanguage-input.md). |
| `STARK_ENABLE_RECOGNIZABLE_EXPAND` | `0` | O(S × L) per match — S suggestions × L regex length | Inject phonetic alternatives into compiled regexes. Requires `RecognizableAlternativesProcessor` in the pipeline. |

Set via environment variables before running your app:

```bash
STARK_ENABLE_VOICE_CLI=1 STARK_ENABLE_RECOGNIZABLE_EXPAND=1 python -m your_app
```

### STARK_ENABLE_RECOGNIZABLE_EXPAND

S.T.A.R.K offers two fuzzy matching approaches. They solve different problems and can be used together:

| | Recognizable Expand | NLDictionaryName (Phonetic Dictionary) |
|---|---|---|
| **Best for** | Fuzzy command keyword matching ("tern on lite" → "turn on light") | Fuzzy named entity parsing ("parish" → "Paris", "лінкін парк" → "Linkin Park") |
| **What it is** | Pattern expansion at match time | A full Object type with its own `did_parse` |
| **What it does** | Widens compiled command regex to accept phonetic variants of recognizable strings | Searches a pre-built phonetic dictionary inside `did_parse`, matching the parameter substring against stored names cross-lingually |
| **How it works** | `"hello"` in pattern → `"(hello\|helo)"` | `"weather in parish"` → `NLCityName.did_parse` → Dictionary.search_in_sentence → finds "Paris" via phonetic similarity |
| **Level** | Pattern matching (before parsing) | Parameter parsing (inside `did_parse`) |
| **Scope** | Static parts of all command patterns | Specific parameter types that subclass `NLDictionaryName` |
| **Data source** | Localizer's recognizable `.strings` bundles | `Dictionary` with `DictionaryStorageMemory` or `DictionaryStorageSQL` |
| **Requires** | `RecognizableAlternativesProcessor` + flag | Subclass `NLDictionaryName`, fill `Dictionary` at build time |
| **Complexity** | O(R × W) generation + O(S) expansion | O(D) lookup per parameter candidate, D = dictionary entries (mode-dependent: EXACT < CONTAINS < FUZZY) |

See [Custom Processors](custom-processors.md) for Recognizable Expand and pipeline setup, and [Phonetic Dictionary](../tools/phonetic-dictionary.md) for NLDictionaryName usage.
