import pytest
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
        self._responses = []
    
    def commands_context_did_receive_response(self, response: Response):
        self._responses.append(response)

@pytest.fixture
def commands_context_flow() -> tuple[CommandsContext, CommandsContextDelegateMock]:
    manager = CommandsManager()
    context = CommandsContext(manager)
    context_delegate = CommandsContextDelegateMock()
    context.delegate = context_delegate
    
    assert len(context_delegate._responses) == 0
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
        
    @manager.new('sleep')
    def sleep():
        return None
        
    @manager.new('repeat')
    def repeat():
        return Response.repeat_last
        
    return context, context_delegate