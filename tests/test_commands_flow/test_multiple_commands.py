from core import Object, Pattern, Response
from general.classproperty import classproperty


class Mock(Object):
    
    parsing_counter = 0
    
    @classproperty
    def pattern(cls):
        return Pattern('*')
    
    def did_parse(self, from_string: str) -> str:
        Mock.parsing_counter += 1
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
    
def test_objects_parse_caching(commands_context_flow):
    manager, context, context_delegate = commands_context_flow
    Pattern.add_parameter_type(Mock)
    
    @manager.new('hello $mock:Mock')
    def hello(mock: Mock): pass
    
    @manager.new('hello $mock:Mock 2')
    def hello2(mock: Mock): pass
    
    @manager.new('hello $mock:Mock 22')
    def hello22(mock: Mock): pass
    
    @manager.new('test $mock:Mock')
    def test(mock: Mock): pass
    
    assert Mock.parsing_counter == 0
    manager.search('hello foobar 22')
    assert Mock.parsing_counter == 1
    manager.search('hello foobar 22')
    assert Mock.parsing_counter == 2
    