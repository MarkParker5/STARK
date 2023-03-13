import pytest


# TODO:issue#2: test delays_reports, threads

def test_basic_search(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    assert len(context_delegate._responses) == 0
    assert len(context._context_queue) == 1
    
    context.process_string('lorem ipsum dolor')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Lorem!'
    assert len(context._context_queue) == 1
    
def test_second_context_layer(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    context.process_string('hello world')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Hello, world!'
    assert len(context._context_queue) == 2
    context_delegate._responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Hi, world!'
    assert len(context._context_queue) == 2
    context_delegate._responses.clear()
    
def test_context_pop_on_not_found(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    context.process_string('hello world')
    assert len(context._context_queue) == 2
    assert len(context_delegate._responses) == 1
    context_delegate._responses.clear()
    
    context.process_string('lorem ipsum dolor')
    assert len(context._context_queue) == 1
    assert len(context_delegate._responses) == 1

def test_context_pop_context_response_action(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    context.process_string('hello world')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Hello, world!'
    assert len(context._context_queue) == 2
    context_delegate._responses.clear()
    
    context.process_string('bye')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Bye, world!'
    assert len(context._context_queue) == 1
    context_delegate._responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate._responses) == 0

@pytest.mark.skip(reason = 'Not implemented yet') # TODO: 
def test_sleep_response_action(commands_context_flow):
    context, context_delegate = commands_context_flow

    context.process_string('sleep')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Sleeping...'
    assert context._last_interaction_time.timestamp() == 0
   
def test_repeat_last_answer_response_action(commands_context_flow):
    context, context_delegate = commands_context_flow
    
    context.process_string('hello world')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Hello, world!'
    context_delegate._responses.clear()
    assert len(context_delegate._responses) == 0
    
    context.process_string('repeat')
    assert len(context_delegate._responses) == 1
    assert context_delegate._responses[0].text == 'Hello, world!'
