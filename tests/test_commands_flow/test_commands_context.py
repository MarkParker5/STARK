import pytest
import config


def test_basic_search(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    assert len(context_delegate.responses) == 0
    assert len(context._context_queue) == 1
    
    context.process_string('lorem ipsum dolor')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Lorem!'
    assert len(context._context_queue) == 1
    
def test_second_context_layer(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('hello world')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
    assert len(context._context_queue) == 2
    context_delegate.responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hi, world!'
    assert len(context._context_queue) == 2
    context_delegate.responses.clear()
    
def test_context_pop_on_not_found(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('hello world')
    assert len(context._context_queue) == 2
    assert len(context_delegate.responses) == 1
    context_delegate.responses.clear()
    
    context.process_string('lorem ipsum dolor')
    assert len(context._context_queue) == 1
    assert len(context_delegate.responses) == 1

def test_context_pop_context_response_action(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('hello world')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
    assert len(context._context_queue) == 2
    context_delegate.responses.clear()
    
    context.process_string('bye')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Bye, world!'
    assert len(context._context_queue) == 1
    context_delegate.responses.clear()
    
    context.process_string('hello')
    assert len(context_delegate.responses) == 0

def test_sleep_response_action(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled

    context.process_string('afk')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Sleeping...'
    assert config.is_afk == True
   
def test_repeat_last_answer_response_action(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('hello world')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
    context_delegate.responses.clear()
    assert len(context_delegate.responses) == 0
    
    context.process_string('repeat')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses[0].text == 'Hello, world!'
