from VICore import VIObject, Pattern, Response
from general.classproperty import classproperty


class VIMock(VIObject):
    
    parsing_counter = 0
    
    @classproperty
    def pattern(cls):
        return Pattern('*')
    
    def did_parse(self, from_string: str) -> str:
        VIMock.parsing_counter += 1
        return from_string

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

def test_repeating_command(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('lorem * dolor')
    def lorem(): 
        return Response(text = 'lorem!')
    
    context.process_string('lorem pisum dolor lorem ipsutest_repeating_commanduum dolor sit amet')
    assert len(context_delegate.responses) == 2
    assert context_delegate.responses[0].text == 'lorem!'
    assert context_delegate.responses[1].text == 'lorem!'

def test_overlapping_commands_less_priority_cut(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('foo bar *')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('* baz')
    def baz(): 
        return Response(text = 'baz!')
    
    result = manager.search('foo bar test baz')
    assert len(result) == 2
    assert result[0].match_result.substring == 'foo bar test'
    assert result[1].match_result.substring == 'baz'

def test_overlapping_commands_priority_cut(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('foo bar *')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('*t baz')
    def baz(): 
        return Response(text = 'baz!')
    
    result = manager.search('foo bar test baz')
    assert len(result) == 2
    assert result[0].match_result.substring == 'foo bar'
    assert result[1].match_result.substring == 'test baz'

def test_overlapping_commands_remove(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    
    @manager.new('foo bar')
    def foobar(): 
        return Response(text = 'foo!')
    
    @manager.new('bar baz')
    def barbaz(): 
        return Response(text = 'baz!')
    
    result = manager.search('foo bar baz')
    assert len(result) == 1
    assert result[0].command == foobar
    
def test_overlapping_commands_remove_inverse(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
     
    @manager.new('bar baz')
    def barbaz(): 
        return Response(text = 'baz!')
    
    @manager.new('foo bar')
    def foobar(): 
        return Response(text = 'foo!')
    
    result = manager.search('foo bar baz')
    assert len(result) == 1
    assert result[0].command == barbaz
    
def test_viobjects_parse_caching(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    Pattern.add_parameter_type(VIMock)
    
    @manager.new('hello $mock:VIMock')
    def hello(mock: VIMock): pass
    
    @manager.new('hello $mock:VIMock 2')
    def hello2(mock: VIMock): pass
    
    @manager.new('hello $mock:VIMock 22')
    def hello22(mock: VIMock): pass
    
    @manager.new('test $mock:VIMock')
    def test(mock: VIMock): pass
    
    assert VIMock.parsing_counter == 0
    manager.search('hello foobar 22')
    assert VIMock.parsing_counter == 1
    manager.search('hello foobar 22')
    assert VIMock.parsing_counter == 2
    