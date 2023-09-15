from core import String, Pattern


def test_pattern():
    assert String.pattern == Pattern('**')
    
def test_parse():
    assert String.parse('')
    assert String.parse('foo bar baz').obj.value == 'foo bar baz'
    
def test_match():
    p = Pattern('foo $bar:String baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == String('qwerty')
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert m
    assert m[0].parameters['bar'] == String('lorem ipsum dolor sit amet')
    
def test_formatted():
    string = String.parse('foo bar baz').obj
    assert str(string) == '<String value: "foo bar baz">'
    assert f'{string}' == 'foo bar baz'