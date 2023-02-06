from VICore import VIWord, Pattern


def test_pattern():
    assert VIWord.pattern == Pattern('*')
    
def test_parse():
    word = VIWord.parse('foo')
    assert word
    assert word.value == 'foo'
    
def test_match():
    p = Pattern('foo $bar:VIWord baz')
    assert p
    
    m = p.match('foo qwerty baz')
    assert m
    assert m.groups['bar'] == 'qwerty'
    
    m = p.match('foo lorem ipsum dolor sit amet baz')
    assert not m
    
def test_formatted():
    assert VIWord.parse('foo').formatted == 'foo'