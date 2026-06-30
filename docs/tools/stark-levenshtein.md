---
description: Fast, Cython-compiled Levenshtein distance and fuzzy substring search for Python, with weighted proximity graphs, prefix/suffix skipping, and in-sentence fuzzy search.
---

# STARK-Levenshtein: Cython Fuzzy String & Substring Matching with Proximity Graphs

## Overview

A from-scratch, Cython-compiled Levenshtein implementation, not a wrapper around an existing library. It does the standard distance/similarity calculation, plus a set of features built specifically for matching real speech and real text, not just comparing two clean strings:

- **In-sentence fuzzy substring search**: find where `s1` appears (or nearly appears) anywhere inside a longer `s2`, with matching spans returned, not just a yes/no.
- **Weighted proximity graphs**: replace the default uniform edit cost with custom per-character weights. STARK ships a phonetic proximity graph out of the box (built for [simplephone](raw-phonetic.md) strings) so a `w`/`f` mix-up costs less than an unrelated substitution.
- **Prefix/suffix skipping**: ignore leading or trailing mismatches, which is what makes substring search work in the first place.
- **Early-return short-circuiting**: stop computing as soon as a threshold is unreachable, instead of always computing the full matrix.

Useful for fuzzy string matching, similarity scoring, and fuzzy substring search anywhere, not just inside S.T.A.R.K. Being Cython-compiled is part of what makes the substring-search and early-return paths viable at all; a pure-Python edit-distance matrix gets slow fast once you're scanning whole sentences instead of comparing two short strings.

### Basic Usage

```python
from stark.tools.levenshtein import (
    levenshtein_distance,
    levenshtein_similarity,
    levenshtein_match,
    levenshtein_distance_substring,
    levenshtein_search_substring,
    SIMPLEPHONE_PROXIMITY_GRAPH, # Is more meaningful to use for simplephone strings, see phonetic tools docs
    SKIP_SPACES_GRAPH, # ignores spaces while matching
)

# Get the Levenshtein distance (lower = more similar, 0 = exact match)
lev = levenshtein_distance(s1="kitten", s2="sitting")

# Get similarity score (0.0 to 1.0, higher = more similar)
sim = levenshtein_similarity(s1="kitten", s2="sitting")

# Check if two strings are similar enough (similarity >= threshold)
is_match = levenshtein_match(s1="kitten", s2="sitting", threshold=0.7)

# Find all substrings in s2 with minimal distance to s1
dist_spans = levenshtein_distance_substring(s1="kitten", s2="the sitting cat")
# Returns: list of (Span, distance)

# Find substrings in s2 where similarity to s1 is above threshold
search_spans = levenshtein_search_substring(s1="kitten", s2="the sitting cat", threshold=0.7)
# Returns: list of (Span, similarity)
```

### Parameters

All functions accept:

- `s1: str` – first string to compare (**required**)
- `s2: str` – second string to compare (**required**)
- `proximity_graph: dict[str, dict[str, float]] | None = None` – custom operation costs instead of default 1. For example, based on phonetic similarity, keyboard proximity, or just to ignore some characters.
- `max_distance: float | None = None` – skip calculation if distance exceeds this value and early_return is True (optional)
- `ignore_prefix: bool = False` – ignore matching prefixes, required for substring search
- `ignore_suffix: bool = False` – ignore matching suffixes, breaks substring search
- `narrow: bool = False` – restrict to shortest possible substring (substring search)
- `early_return: bool = True` – return as soon as threshold is met (faster). False value is for debug only.
- `lower: bool = False` – compare strings as lowercase

Functions with a `threshold` parameter:
- `threshold: float = 0` – similarity threshold for match/search; used to calc max_distance, which stops the calculation early if distance exceeds this value to improve performance

### Constants

```python
type ProximityGraph = dict[str, dict[str, float]]
PROX_MED = 0.5
PROX_LOW = 0.25
PROX_MIN = 0.01
SIMPLEPHONE_PROXIMITY_GRAPH: ProximityGraph = {
    "w": {"f": PROX_MED, "a": PROX_LOW, "y": PROX_LOW},
    "y": {"a": PROX_LOW, "w": PROX_LOW},
    "a": {"y": PROX_LOW, "w": PROX_LOW, "-": PROX_LOW},  # '-' for deletion
    "f": {"w": PROX_MED},
    " ": {"-": PROX_MIN},  # ignore spaces
    "-": {"a": PROX_LOW, " ": PROX_MIN},  # insertion
}
SKIP_SPACES_GRAPH = {" ": {"-": PROX_MIN}, "-": {" ": PROX_MIN}}
```

---

For more advanced usage, see the source code or use your IDE's autocomplete.
