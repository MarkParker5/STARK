from VICore import Response


def test_multiple_commands(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('foo bar')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('lorem * dolor')
    def lorem(): 
        return Response(text = 'lorem!')
    
    context.process_string('foo bar lorem ipsum dolor')
    assert len(context_delegate.responses) == 2
    assert context_delegate.responses[0].text == 'foo!'
    assert context_delegate.responses[1].text == 'lorem!'

def test_repeating_command():
    pass

def test_overlapping_commands_less_priority_cut():
    pass

def test_overlapping_commands_priority_cut():
    pass

def test_overlapping_commands_remove():
    pass

def test_viobjects_parse_caching():
    pass