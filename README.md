# A.R.C.H.I.E.
## Voice assistant, smart home hub, media center and smart tv

### Project structure:
 - #### VICore - Core, base classes
   - Command
   - CommandsManager
   - SearchResult
   - Response
   - ThreadData
   - Pattern
   - VIObject and subclasses
 - #### Controls - Responsible for user interaction
   - Control(ABC)
   - VoiceAssistant
   - TelegramBot
   - RemoteControl
   - Django
 - #### Features - Possibilities, set of functions
 - #### General - For helper classes
 - #### hardware - Control system and hardware

### Root files:
 - **start.py** - entry point
 - **config.example.py** - file for settings. Copy as config.py and type own paraneters
 - **helper.py** - use in terminal for creating new modules, commands, features, controls, etc.
 - **dependences.txt** - list of all dependences (Python version and libraries)
