from core import Word, Pattern


def test_pattern():
    assert Word.pattern == Pattern('*')
    
def test_parse():
    word = Word.parse('foo').obj
    assert word
    assert word.value == 'foo'
    
def test_match():
    p = Pattern('foo $bar:Word baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == Word('qwerty')
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert not m
    
def test_formatted():
    string = Word.parse('foo').obj
    assert str(string) == '<Word value: "foo">'
    assert f'{string}' == 'foo'