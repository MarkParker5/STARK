from VICore import CommandsContext
from VoiceAssistant import VoiceAssistant
from features import default


# TODO: typer
if __name__ == '__main__':
    cm = CommandsContext(commands_manager = default)
    va = VoiceAssistant(commands_context = cm)
    
    va.start()
