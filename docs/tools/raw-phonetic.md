# Raw Phonetic Tools: IPA & Simplephone

## Overview

These tools convert text to phonetic representations for fuzzy matching, name lookup, and cross-language search.
They power the phonetic matching in the [Dictionary Tool](./phonetic-dictionary.md) and are often used together (simplephone code of the phonetic transcription) for best results.

- `phonetic`: Converts text in any language to a simplified Latin transcription using IPA (International Phonetic Alphabet), currently implemented using espeak-ng (requires [libespeak-ng binary](https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md#installation) installed in the system).
- `simplephone`: Further reduces a transcription (or plain English text) to a simple, language-agnostic phonetic code for fast, robust matching.

## Basic Usage

```python
from stark.tools.phonetic.ipa import phonetic
from stark.tools.phonetic.simplephone import simplephone

# Convert ukrainian to simplified Latin phonetic transcription (IPA-based)
ipa = phonetic("Лінкін Парк", "uk")  # e.g. "Лінкін Парк" → "linkin park"

# Convert to simplephone code (robust, language-agnostic)
sp = simplephone("Linkin Park")      # e.g. "linkin park" → "LNKNPARK"

# Combine for best fuzzy matching (recommended for cross-language)
sp_combined = simplephone(phonetic("Лінкін Парк", "uk"))  # → "LNKNPARK"
```

## Function Reference

### def phonetic

```python
def phonetic(text: str, language_code: str) -> str
```

- Converts a string to a simplified Latin phonetic transcription using IPA via espeak-ng.
- Handles many languages (see espeak-ng docs for supported codes).
- Used for cross-language and accent-insensitive matching.

**Parameters:**
- `text`: Input string.
- `language_code`: BCP-47 or ISO language code (e.g. `"en"`, `"uk"`, `"de"`).

**Returns:**
Simplified Latin transcription as a string.

### def simplephone

```python
def simplephone(text: str, glue: str = " ", sep: str = string.whitespace) -> str | None
```

- Converts a string to a simple, language-agnostic phonetic code.
- Inspired by Caverphone, Soundex, and Kölner Phonetik.
- Ignores spaces, strips non-alphabetic characters, and normalizes similar sounds.

**Parameters:**
- `text`: Input string consisting of latin characters.
- `glue`: Separator for joining words (default: space).
- `sep`: Characters to treat as word separators (default: whitespace).

**Returns:**
Simplephone code as a string, or `None` if input is empty.

## Typical Usage Pattern

For best fuzzy matching (especially cross-language), use both together:

```python
# For English input
a = simplephone(phonetic("Linkin Park", "en"))  # → "LNKNPARK"

# For Ukrainian input
b = simplephone(phonetic("Лінкін Парк", "uk"))  # → "LNKNPARK"

a == b # True
```

This enables matching names and words across different languages and spellings.

## More fuzzyness

For even more fuzzyness, consider using the levenshtein distance with the default proximity graph for simplephone (`SIMPLEPHONE_PROXIMITY_GRAPH`). For details see [STARK's Levenshtein implementation](./stark-levenshtein.md)

## Notes

- `phonetic` requires [espeak-ng](https://github.com/espeak-ng/espeak-ng) installed on your system.
- These functions are used internally by the Dictionary Tool for phonetic and fuzzy lookup.
- For more details, see the source code or use your IDE's autocomplete.
