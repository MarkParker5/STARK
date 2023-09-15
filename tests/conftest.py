from typing import AsyncGenerator
import time
import contextlib
import pytest
import asyncer
from general.dependencies import DependencyManager
from core import (
    CommandsManager,
    CommandsContext,
    CommandsContextDelegate, 
    Response,
    ResponseHandler,
    Word
)
from voice_assistant import VoiceAssistant


class CommandsContextDelegateMock(CommandsContextDelegate):
    
    responses: list[Response]
    
    def __init__(self):
        self.responses = []
    
    def commands_context_did_receive_response(self, response: Response):
        self.responses.append(response)
        
class SpeechRecognizerMock:
    is_recognizing: bool = False
    
    def start_listening(self): pass
    def stop_listening(self): pass
        
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
async def commands_context_flow():
    @contextlib.asynccontextmanager
    async def _commands_context_flow() -> AsyncGenerator[tuple[CommandsManager, CommandsContext, CommandsContextDelegateMock], None]:
        async with asyncer.create_task_group() as main_task_group:
            dependencies = DependencyManager()
            manager = CommandsManager()
            context = CommandsContext(main_task_group, manager, dependencies)
            context_delegate = CommandsContextDelegateMock()
            context.delegate = context_delegate
            
            assert len(context_delegate.responses) == 0
            assert len(context._context_queue) == 1
            
            main_task_group.soonify(context.handle_responses)()
            yield (manager, context, context_delegate)
            context.stop()
    return _commands_context_flow

@pytest.fixture
async def commands_context_flow_filled(commands_context_flow):
    @contextlib.asynccontextmanager
    async def _commands_context_flow_filled() -> AsyncGenerator[tuple[CommandsContext, CommandsContextDelegateMock], None]:
        async with commands_context_flow() as (manager, context, context_delegate):
    
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
            def bye_context(name: Word, handler: ResponseHandler):
                handler.pop_context()
                return Response(
                    text = f'Bye, {name}!'
                ) 
            
            @manager.new('hello $name:Word')
            def hello(name: Word):
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
    
            yield (context, context_delegate)
            
    return _commands_context_flow_filled

@pytest.fixture
async def voice_assistant(commands_context_flow_filled):
    context, _ = commands_context_flow_filled
    voice_assistant = VoiceAssistant(
        speech_recognizer = SpeechRecognizerMock(),
        speech_synthesizer = SpeechSynthesizerMock(),
        commands_context = context
    )
    voice_assistant.start()
    
    yield voice_assistant
