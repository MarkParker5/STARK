from VICore import VIString, Pattern


def test_pattern():
    assert VIString.pattern == Pattern('**')
    
def test_parse():
    assert VIString.parse('')
    assert VIString.parse('foo bar baz').obj.value == 'foo bar baz'
    
def test_match():
    p = Pattern('foo $bar:VIString baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == VIString('qwerty')
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert m
    assert m[0].parameters['bar'] == VIString('lorem ipsum dolor sit amet')
    
def test_formatted():
    string = VIString.parse('foo bar baz').obj
    assert str(string) == '<VIString value: "foo bar baz">'
    assert f'{string}' == 'foo bar baz'