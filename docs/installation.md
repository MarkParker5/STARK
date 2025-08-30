# Installation

This guide will walk you through the installation of the STARK framework and its associated extras. You can use either pip or poetry for the installation. Let's dive right in!

## Prerequisites

Ensure you have Python 3.12 or newer installed. You can verify this with:
```bash
python --version
```

On some systems, you may need to use the `python3` command instead of `python`:
```bash
python3 --version
```

### Avaiable Extras

The STARK framework offers several extras, which are default implementations for its protocols, to facilitate integration with various tools. These extras include:

- **all**: Installs all default implementations. Recommended if you're not well-versed in dependency management.
- **vosk**: [Vosk](https://alphacephei.com/vosk/) (offline speech recognition) implementation of SpeechRecognizer protocol.
- **gcloud**: [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) implementation of SpeechSynthesizer protocol.
- **silero**: [Silero](https://github.com/snakers4/silero-models) Models (offline) implementation of SpeechSynthesizer.
- **sound**: Required utilities for processing sound: `sounddevice` and `soundfile`.

## Installation with pip

To install the base version of STARK:

```bash
pip install stark-engine
```

To install any of the extras:

```bash
pip install stark-engine[all]
pip install stark-engine[gcloud]
pip install stark-engine[vosk]
pip install stark-engine[silero]
pip install stark-engine[sound]
```

If you encounter the error `zsh: no matches found`, simply enclose the package name in quotes:

```zsh
pip install "stark-engine[all]"
pip install "stark-engine[gcloud]"
pip install "stark-engine[vosk]"
pip install "stark-engine[silero]"
pip install "stark-engine[sound]"
```

## Installation with poetry

If you, like me, prefer using [poetry](https://python-poetry.org) to manage dependencies along with a virtual environment, simply replace `pip install` with `poetry add`.



``` bash
poetry add stark-engine
poetry add stark-engine[all]
poetry add stark-engine[gcloud]
poetry add stark-engine[vosk]
poetry add stark-engine[silero]
poetry add stark-engine[sound]
```

If you encounter the error `zsh: no matches found`, simply enclose the package name in quotes:

```zsh
poetry add "stark-engine[all]"
poetry add "stark-engine[gcloud]"
poetry add "stark-engine[vosk]"
poetry add "stark-engine[silero]"
poetry add "stark-engine[sound]"
```

---

With the STARK framework installed and the desired extras in place, you're all set to develop powerful voice-driven applications. Dive into the documentation, experiment, and build great things!
