# S.T.A.R.K.

**Speech and Text Algorithmic Recognition Kit**

Modern, advanced, and fast framework for creating natural language (especially voice) interfaces. Like [FastAPI](https://fastapi.tiangolo.com/), but with speech instead of http. 

Check [docs](https://stark.markparker.me/) for more information.

# Overview

Welcome to the S.T.A.R.K. Docs project, a comprehensive toolkit for building custom voice assistants. This project provides a robust and flexible framework for creating voice assistants that can be tailored to specific use cases. The project includes a variety of features such as navigation, search, and social media integration. The core of the project is the "stark-engine", a Python package that provides the necessary tools and functionalities for building and managing voice assistants.

The project also includes a series of tests to ensure the functionality and reliability of the voice assistant program. These tests cover a wide range of scenarios, from testing background commands and context flows to serializing and deserializing commands using JSON. The project also includes a website, stark.markparker.me, which serves as the main hub for accessing the tools and resources provided by the project.

# Technologies and Frameworks

The S.T.A.R.K. Docs project utilizes a variety of technologies and frameworks to provide a robust and flexible toolkit for building voice assistants. Here are some of the key technologies and frameworks used in this project:

- **Python**: The core language used for the project. The stark-engine package and all the tests are written in Python.
- **MkDocs**: Used for building the S.T.A.R.K. Docs website.
- **Google Cloud Text-to-Speech API**: Used for synthesizing speech from text.
- **Vosk Library**: Used for speech recognition.
- **Sounddevice Library**: Used for playing synthesized speech.
- **Anyio**: Used for managing asynchronous tasks.
- **Pydantic**: Used for data validation and settings management.
- **Silero Models**: Used for speech synthesis.

# Installation

This guide will walk you through the process of setting up the project on your local machine.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.10.
- You have a basic understanding of using the command line.

## Installing the Project

To install the project, follow these steps:

1. Clone the repository to your local machine:

```bash
git clone https://github.com/MarkParker5/STARK.git
```

2. Navigate to the project directory:

```bash
cd STARK
```

3. Install the required Python packages:

```bash
pip install pydantic==1.10.4 asyncer==0.0.2
```

Optional dependencies include numpy, sounddevice, soundfile, vosk, google-cloud-texttospeech, torch, mkdocs-material, and mkdocs-git-revision-date-localized-plugin. You can install these as needed.

Development dependencies include pytest, mypy, pytest-asyncio, pytest-trio, and pytest-repeat. You can install these if you plan to contribute to the project.

4. Install the stark package:

```bash
pip install stark-engine
```
