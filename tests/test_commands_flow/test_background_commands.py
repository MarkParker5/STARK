
def test_background_command(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('background min')
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses.pop(0).text == 'Starting background task'
    assert len(context._threads) == 1
    
    context._check_threads()
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses.pop(0).text == 'Finished background task'
    
def test_background_with_multiple_responses(commands_context_flow_filled):
    context, context_delegate = commands_context_flow_filled
    
    context.process_string('background multiple responses')
    
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses.pop(0).text == 'Starting long background task'
    assert len(context._threads) == 1
    
    responses = ['First response', 'Second response']
    
    while context._threads[0].thread.is_alive():
        if context_delegate.responses:
            assert len(context_delegate.responses) == 1
            assert context_delegate.responses.pop(0).text == responses.pop(0)
    
    assert len(context_delegate.responses) == 0
    assert len(responses) == 0
    
    context._check_threads()
    assert len(context_delegate.responses) == 1
    assert context_delegate.responses.pop(0).text == 'Finished long background task'
