from ArchieCore import Command, Response

@Command.new(['привет*',])
def hello(params):
    voice = text = 'Привет'
    return Response(text = text, voice = voice)
