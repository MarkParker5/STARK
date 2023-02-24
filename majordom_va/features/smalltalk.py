from VICore import CommandsManager, Response


manager = CommandsManager('smalltalk')

@manager.new('привет*')
def hello():
    voice = text = 'Привет'
    return Response(text = text, voice = voice)