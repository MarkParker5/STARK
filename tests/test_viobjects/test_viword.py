from VICore import VIWord, Pattern


def test_pattern():
    assert VIWord.pattern == Pattern('*')
    
def test_parse():
    word = VIWord.parse('foo').obj
    assert word
    assert word.value == 'foo'
    
def test_match():
    p = Pattern('foo $bar:VIWord baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == VIWord('qwerty')
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert not m
    
def test_formatted():
    string = VIWord.parse('foo').obj
    assert str(string) == '<VIWord value: "foo">'
    assert f'{string}' == 'foo'