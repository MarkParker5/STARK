import pytest
import config
import time
from VICore import (
    CommandsManager,
    CommandsContext,
    CommandsContextDelegate, 
    Response,
    ResponseHandler,
    VIWord
)
from VoiceAssistant import VoiceAssistant


class CommandsContextDelegateMock(CommandsContextDelegate):
    
    responses: list[Response]
    
    def __init__(self):
        self.responses = []
    
    def commands_context_did_receive_response(self, response: Response):
        self.responses.append(response)
        
class SpeechRecognizerMock:
    is_recognizing: bool = False
    
    async def start_listening(self): pass
    async def stop_listening(self): pass
        
class SpeechSynthesizerResultMock:
    def play(self): pass
    
    def __init__(self, text: str):
        self.text = text
    
class SpeechSynthesizerMock:
    
    def __init__(self):
        self.results = []
    
    def synthesize(self, text: str) -> SpeechSynthesizerResultMock:
        result = SpeechSynthesizerResultMock(text)
        self.results.append(result)
        return result

@pytest.fixture
def commands_context_flow() -> tuple[CommandsManager, CommandsContext, CommandsContextDelegateMock]:
    manager = CommandsManager()
    context = CommandsContext(manager)
    context_delegate = CommandsContextDelegateMock()
    context.delegate = context_delegate
    
    assert len(context_delegate.responses) == 0
    assert len(context._context_queue) == 1
    
    return manager, context, context_delegate

@pytest.fixture
def commands_context_flow_filled(commands_context_flow) -> tuple[CommandsContext, CommandsContextDelegateMock]:
    
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('test')
    def test(): 
        return Response()
    
    @manager.new('lorem * dolor')
    def lorem(): 
        return Response(text = 'Lorem!', voice = 'Lorem!')
    
    @manager.new('hello', hidden = True)
    def hello_context(**params):
        voice = text = f'Hi, {params["name"]}!' 
        return Response(text = text, voice = voice)
    
    @manager.new('bye', hidden = True)
    def bye_context(name: VIWord, handler: ResponseHandler):
        handler.pop_context()
        return Response(
            text = f'Bye, {name}!'
        ) 
    
    @manager.new('hello $name:VIWord')
    def hello(name: VIWord):
        text = voice = f'Hello, {name}!' 
        return Response(
            text = text,
            voice = voice,
            commands = [hello_context, bye_context],
            parameters = {'name': name}
        )
        
    @manager.new('repeat')
    def repeat():
        return Response.repeat_last
    
    # background commands
    
    @manager.new('background min')
    @manager.background(Response(text = 'Starting background task', voice = 'Starting background task'))
    def background():
        text = voice = 'Finished background task'
        return Response(text = text, voice = voice)
        
    @manager.new('background multiple responses')
    @manager.background(Response(text = 'Starting long background task'))
    def background_multiple_responses(handler: ResponseHandler):
        time.sleep(0.05)
        handler.process_response(Response(text = 'First response'))
        time.sleep(0.05)
        handler.process_response(Response(text = 'Second response'))
        time.sleep(0.05)
        text = voice = 'Finished long background task'
        return Response(text = text, voice = voice)
    
    @manager.new('background needs input')
    @manager.background(Response(text = 'Starting long background task'))
    def background_needs_input(handler: ResponseHandler):
        time.sleep(0.01)
        
        for text in ['First response', 'Second response', 'Third response']:
            handler.process_response(Response(text = text, voice = text))
            
        text = 'Needs input'
        handler.process_response(Response(text = text, voice = text, needs_user_input = True))
        
        for text in ['Fourth response', 'Fifth response', 'Sixth response']:
            handler.process_response(Response(text = text, voice = text))
        
        text = voice = 'Finished long background task'
        return Response(text = text, voice = voice)
    
    @manager.new('background with context')
    @manager.background(Response(text = 'Starting long background task', voice = 'Starting long background task'))
    def background_multiple_contexts(handler: ResponseHandler):
        time.sleep(0.01)
        text = voice = 'Finished long background task'
        return Response(text = text, voice = voice, commands = [hello_context, bye_context], parameters = {'name': 'John'})
    
    @manager.new('background remove response')
    @manager.background(Response(text = 'Starting long background task'))
    def background_remove_response(handler: ResponseHandler):
        time.sleep(0.01)
        response = Response(text = 'Deleted response', voice = 'Deleted response')
        handler.process_response(response)
        time.sleep(0.05)
        handler.remove_response(response)
        return None
        
    return context, context_delegate

@pytest.fixture
def voice_assistant(commands_context_flow_filled):
    context, _ = commands_context_flow_filled
    voice_assistant = VoiceAssistant(
        speech_recognizer = SpeechRecognizerMock(),
        speech_synthesizer = SpeechSynthesizerMock(),
        commands_context = context
    )
    voice_assistant.start()
    return voice_assistant