# from VICore import (
#     CommandsManager,
#     CommandsContext,
#     CommandsContextDelegate, 
#     Response,
#     ResponseAction
# )


# TODO: test delays_reports, threads, memory, response_actions

def test_basic_search(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    assert len(context_delegate.responses) == 0
    assert len(context.context_queue) == 1
    
    context.process_string('lorem ipsum dolor')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Lorem!'
    assert len(context.context_queue) == 1
    
def test_context_layers(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    # test second context layer
    
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
    
    # test popping context layer via response action
    
    context.process_string('bye')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Bye, world!'
    assert len(context.context_queue) == 1
    context_delegate.responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate.responses) == 0
    
    # test popping context layer when command not found
    
    context.process_string('hello world')
    assert len(context.context_queue) == 2
    assert len(context_delegate.responses) == 1
    context_delegate.responses.clear()
    
    context.process_string('lorem ipsum dolor')
    assert len(context.context_queue) == 1
    assert len(context_delegate.responses) == 1