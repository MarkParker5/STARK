from VICore import CommandsManager, CommandsContext, CommandsContextDelegate, Response


class CommandsContextDelegateMock(CommandsContextDelegate):
    
    responses: list[Response] = []
    
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
    