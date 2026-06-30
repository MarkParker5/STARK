---
description: Cross-language phonetic name and keyword lookup for Python. Find misspelled, accented, or transliterated names (e.g. Cyrillic to Latin) with fuzzy and exact matching.
---

# Phonetic Dictionary: Cross-Language Name & Keyword Lookup

> NOTE: requires an IPA provider. Default is `EspeakIpaProvider` ([libespeak-ng binary](https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md#installation) installed in the system). For latin-only use cases, `LatinPassthroughProvider` works without external dependencies, is faster, but less accurate. See [raw-phonetic.md](raw-phonetic.md) for more details.

## Overview

### Basic Lookup

Create a dictionary in memory and add an entry:
```python
dictionary = Dictionary(storage=DictionaryStorageMemory())
dictionary.write_one('en', "Linkin Park", {"id": 2017})
```

Then you can look up names by different spellings, homophones, or even cross-language phonetic similarity:
```python
matches = dictionary.lookup("linkoln perk", 'en') # misspelled case
matches[0].metadata  # {"id": 2017})

matches = dictionary.lookup("лінкін парк", 'uk') # ukrainian spelling of Linkin Park
matches[0].metadata  # {"id": 2017})
```

### Search in Sentence

You can also scan an entire sentence for names from a dictionary:

```python
dictionary.search_in_sentence("good morning play linkin park on spotify", 'en')
```

Both `lookup` and `search_in_sentence` receive two optional parameters: `mode: LookupMode = .AUTO` and `field: LookupField = .PHONETIC`.

```python
class LookupMode(Enum):
    EXACT = auto()  # the fastest
    CONTAINS = auto()  # fast
    FUZZY = auto()  # slow, not recommended at 10K+ entries
    AUTO = auto()  # recommended: tries modes sequentially until match with some dict-size limits

class LookupField(Enum):
    NAME = auto()  # search by original name, only same lang is reasonable
    PHONETIC = auto()  # search by phonetic similarity, cross-lang support
```

### Sorting

Also, there are `lookup_sorted` and `search_in_sentence_sorted` methods that automatically sort results by levenshtein distance. These might add a noticeable overhead when many entries are matched (starting from magnitude of a hundred). In most cases, it's better to use the not sorted version, check results amount, and then sort them manually if needed. Example of levenshtein sort:

```python
sorted(
    matches,
    key=lambda item: levenshtein_similarity( # sort by the original name for same languages
        s1=name_candidate,
        s2=item.name,
    ) if item.language_code == language_code else levenshtein_similarity( # sort by phonetic similarity for cross-language
        s1=transcription(name_candidate, language_code),
        s2=item.phonetic,
    ),
    reverse=True,
)
```

> More details about levenshtein for fuzzy string matching [here](./stark-levenshtein.md) page.

But in many cases, domain-specific sorting and filtering is the best approach. For example, in navigator app you can prioritize names that are closer to the user's location. For example, Georgia the state for american users, but Georgia the country for european.

## Using with NLDictionaryName

You can use NLDictionaryName to parse and match names from a Dictionary. It has already implemented `did_parse`, so no need to implement it yourself.

```python
from stark.tools.dictionary.dictionary import Dictionary
from stark.tools.dictionary.nl_dictionary_name import NLDictionaryName
from stark.tools.dictionary.storage import DictionaryStorageMemory

class NLCityName(NLDictionaryName):
    dictionary = Dictionary(storage=DictionaryStorageMemory()) # any NLDictionaryName must implement dictionary: Dictionary

# Fill the dictionary as usual
NLCityName.dictionary.clear()
NLCityName.dictionary.write_one("de", "Nürnberg", {"coords": (49.45, 11.08)})
NLCityName.dictionary.write_one("en", "London",   {"coords": (51.51, -0.13)})
NLCityName.dictionary.write_one("en", "Paris",    {"coords": (48.85, 2.35 )})
NLCityName.dictionary.write_one("cs", "Praha",    {"coords": (50.08, 14.44)})

@manager.new('weather in $city:NLCityName')
def hello(weather: NLCityName):
    print(weather.value[0].item.metadata["coords"]) # (48.85, 2.35) for "weather in parish"
```

Data model overview:

```python
class NLDictionaryName:
    value: list[LookupResult]
    dictionary: Dictionary

class LookupResult:
    span: Span
    item: DictionaryItem

@dataclass
class DictionaryItem:
    name: str
    phonetic: str
    simple_phonetic: str
    language_code: str
    metadata: Metadata # dict[str, object]
```

Inspect your IDE suggestions and the source code (most modern editors support "go to definition" feature) for more details.

## Automatic [Corrections](corrections.md) Generation

Corrections is a matching feature that widens command pattern to accept translation/phonetic variants of known keywords. When STT or user input contains a misspelling or phonetic approximation, this feature injects the variant into the compiled pattern so the command still matches.

See [Corrections](corrections.md) for how Dictionary integrates with the corrections pipeline.

## Encapsulate Storage and Filling Logic

You can encapsulate storage and filling logic in a single class:

```python
class MyDictionary(Dictionary):
    def __init__(self):
        super().__init__(storage=DictionaryStorageSQL("sqlite:///my-phonetic-dictionary.db"))

    async def build(self):
        self.write_all(...)  # Fill from files, db, or API

class NLExampleDictionaryName(NLObject):
    dictionary = MyDictionary()
```

## Building Example

While you can modify a Dictionary even in runtime, the best approach is to fill the dictionary at build stage if possible, since writing might be slow for large dictionaries (especially starting from magnitudes of thousands). There is the example main.py that uses [typer](https://typer.tiangolo.com) to add `build` and `run` cli commands to your app.

```python
import typer

cli = typer.Typer()

@cli.command()
def build():
    """Build the project. See typer docs for better CLI with features like progress bars and logging."""
    print("Building...")
    NLExampleDictionaryName.dictionary.build_if_needed() # fill the sqlite file once during the build stage, not at runtime
    SomeOtherDictionary.build() # or force re-build on each call
    # etc
    print("Done")


@cli.command()
def run():
    """Run your main app here."""
    pass


if __name__ == "__main__":
    cli()
```
