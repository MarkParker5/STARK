# Feature Flags

S.T.A.R.K uses environment variables to enable or disable experimental and optional features.

## Available Flags

| Flag | Default | Description |
|------|---------|-------------|
| `STARK_ENABLE_VOICE_CLI` | `0` | Print voice input/output in terminal. Useful for debugging without a GUI. See [Voice Assistant](../voice-assistant.md). |
| `STARK_ENABLE_MULTILANG_MATRIX` | `1` | Enable matrix cross-language matching across alternative transcription tracks. When a `TranscriptionString` carries alternative texts from different language models, try each track against its language's command patterns. If disabled, only the primary track is used. See [Localizing Parsing](../localization-and-multi-language/localizing-parsing.md). |
| `STARK_ENABLE_RECOGNIZABLE_EXPAND` | `0` | Inject phonetic suggestion variants into compiled pattern regexes before matching based on localisation strings (on the *recognizable strings*, see [Localizing Parsing](../localization-and-multi-language/localizing-parsing.md)). Experimental. |
| `STARK_ENABLE_MULTILANG_PHONETIC_OVERLAP` | `0` | Use phonetic Levenshtein to resolve overlapping matches across alternative tracks when timestamps are not available. If disabled, only one matched track is used. Experimental. See [Localizing Parsing](../localization-and-multi-language/localizing-parsing.md). |

## Setting Flags

Set via environment variables before running your app:

```bash
STARK_ENABLE_VOICE_CLI=1 STARK_ENABLE_RECOGNIZABLE_EXPAND=1 python -m your_app
```

Or in code before importing STARK:

```python
import os
os.environ["STARK_ENABLE_VOICE_CLI"] = "1"
```
