from VICore import (
    CommandsManager,
    CommandsContext,
    CommandsContextDelegate, 
    Response,
    ResponseAction
)


# TODO: test delays_reports, threads, memory, response_actions

class CommandsContextDelegateMock(CommandsContextDelegate):
    
    responses: list[Response]
    
    def __init__(self):
        self.responses = []
    
    def commands_context_did_receive_response(self, response: Response):
        self.responses.append(response)

def test_basic_search():
    manager = CommandsManager()
    context = CommandsContext(manager)
    context_delegate = CommandsContextDelegateMock()
    context.delegate = context_delegate
    
    assert len(context_delegate.responses) == 0
    assert len(context.context_queue) == 1
    
    @manager.new(['test'])
    def test(): pass
    
    @manager.new(['lorem * dolor'])
    def lorem(): pass
    
    @manager.new(['hello $name:VIWord'])
    def hello(params): return Response(text = f'Hello, {params["name"]}!')
    
    context.process_string('hello world')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
    assert len(context.context_queue) == 1
    
def test_context_layers():
    manager = CommandsManager()
    context = CommandsContext(manager)
    context_delegate = CommandsContextDelegateMock()
    context.delegate = context_delegate
    
    assert len(context_delegate.responses) == 0
    assert len(context.context_queue) == 1
    
    @manager.new(['test'])
    def test(): pass
    
    @manager.new(['lorem * dolor'])
    def lorem(): pass
    
    @manager.new(['hello'], hidden = True)
    def hello_context(params): 
        return Response(text = f'Hi, {params["name"]}!')
    
    @manager.new(['bye'], hidden = True)
    def bye_context(params): 
        return Response(
            text = f'Bye, {params["name"]}!',
            actions = [ResponseAction.popContext]
        ) 
    
    @manager.new(['hello $name:VIWord'])
    def hello(params): 
        return Response(
            text = f'Hello, {params["name"]}!',
            commands = [hello_context, bye_context],
            parameters = {'name': params['name']}
        )
    
    context.process_string('hello world')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
    assert len(context.context_queue) == 2
    context_delegate.responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hi, world!'
    assert len(context.context_queue) == 2
    context_delegate.responses.clear()
    
    context.process_string('bye')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Bye, world!'
    assert len(context.context_queue) == 1
    context_delegate.responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate.responses) == 0
    