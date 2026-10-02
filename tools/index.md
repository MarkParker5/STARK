# Tools

S.T.A.R.K. is a framework, but several of its pieces work entirely on their own. No `CommandsManager`, no pattern matching, nothing else from the framework required. This page indexes what you can use solo, grouped by what they actually are.

## Phonetic Matching (Core S.T.A.R.K. Features)

These aren't side utilities bolted on for convenience. Cross-language phonetic matching is core to how S.T.A.R.K. understands misspoken, misspelled, or transliterated input, and it's built on a modular design, so the pieces happen to work standalone too:

- **[Phonetic Dictionary](https://stark.markparker.me/tools/phonetic-dictionary/index.md)**: cross-language name and keyword lookup. Find "Linkin Park" whether it's typed, misspelled, or transliterated from Cyrillic.
- **[Corrections](https://stark.markparker.me/tools/corrections/index.md)**: widens command patterns to accept phonetic and misspelled variants automatically, based on dictionary lookups.

## Raw Standalone Tools

The lower-level building blocks the features above are built on. S.T.A.R.K. uses them internally, and they're just as useful pulled out on their own:

- **[Raw Phonetic Tools](https://stark.markparker.me/tools/raw-phonetic/index.md)**: IPA transcription and simplephone conversion, the layer the dictionary and corrections build on.
- **[Levenshtein](https://stark.markparker.me/tools/stark-levenshtein/index.md)**: a from-scratch, Cython-compiled fuzzy string and substring matcher, with weighted proximity graphs and in-sentence search.
- **[Sliding Window Parser](https://stark.markparker.me/tools/sliding-window-parser/index.md)**: extract parameters from free text using a parser function, even when it only matches part of the input.

## Speech (STT/TTS)

Recognition and synthesis are separate, swappable interfaces. Use either without touching commands at all:

- **[Speech Recognition (STT)](https://stark.markparker.me/tools/speech-recognition/index.md)**: the `SpeechRecognizer` protocol, ready offline implementations (Vosk), and how to add your own backend.
- **[Speech Synthesis (TTS)](https://stark.markparker.me/tools/speech-synthesis/index.md)**: the `SpeechSynthesizer` protocol, ready implementations (Silero, Google Cloud), and how to add your own backend.

______________________________________________________________________

Building something with one of these outside of S.T.A.R.K. entirely? [Tell us in Discussions](https://github.com/MarkParker5/STARK/discussions), it's exactly the kind of thing worth knowing about, and we need all the feedback we can get to make S.T.A.R.K. better.
