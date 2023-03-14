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


class CommandsContextDelegateMock(CommandsContextDelegate):
    
    responses: list[Response]
    
    def __init__(self):
        self.responses = []
    
    def commands_context_did_receive_response(self, response: Response):
        self.responses.append(response)

@pytest.fixture
def commands_context_flow() -> tuple[CommandsContext, CommandsContextDelegateMock]:
    manager = CommandsManager()
    context = CommandsContext(manager)
    context_delegate = CommandsContextDelegateMock()
    context.delegate = context_delegate
    
    assert len(context_delegate.responses) == 0
    assert len(context._context_queue) == 1
    
    @manager.new('test')
    def test(): 
        return Response()
    
    @manager.new('lorem * dolor')
    def lorem(): 
        return Response(text = 'Lorem!')
    
    @manager.new('hello', hidden = True)
    def hello_context(**params): 
        return Response(text = f'Hi, {params["name"]}!')
    
    @manager.new('bye', hidden = True)
    def bye_context(name: VIWord, handler: ResponseHandler):
        handler.pop_context()
        return Response(
            text = f'Bye, {name}!'
        ) 
    
    @manager.new('hello $name:VIWord')
    def hello(name: VIWord): 
        return Response(
            text = f'Hello, {name}!',
            commands = [hello_context, bye_context],
            parameters = {'name': name}
        )
        
    @manager.new('afk')
    def afk():
        config.is_afk = True
        return Response(text = 'Sleeping...')
        
    @manager.new('repeat')
    def repeat():
        return Response.repeat_last
    
    # background commands
    
    @manager.new('background min')
    @manager.background(Response(text = 'Starting background task'))
    def background():
        return Response(text = 'Finished background task')
        
    @manager.new('background multiple responses')
    @manager.background(Response(text = 'Starting long background task'))
    def background_multiple_responses(handler: ResponseHandler):
        time.sleep(0.05)
        handler.process_response(Response(text = 'First response'))
        time.sleep(0.05)
        handler.process_response(Response(text = 'Second response'))
        time.sleep(0.05)
        return Response(text = 'Finished long background task')
        
    return context, context_delegate