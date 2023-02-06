from VICore import VIString, Pattern


def test_pattern():
    assert VIString.pattern == Pattern('**')
    
def test_parse():
    assert VIString.parse('')
    assert VIString.parse('foo bar baz').value == 'foo bar baz'
    
def test_match():
    p = Pattern('foo $bar:VIString baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m.groups['bar'] == 'qwerty'
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert m
    assert m.groups['bar'] == 'lorem ipsum dolor sit amet'
    
def test_formatted():
    assert VIString.parse('foo bar baz').formatted == 'foo bar baz'