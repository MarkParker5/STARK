from core import Word, Pattern


def test_pattern():
    assert Word.pattern == Pattern('*')
    
async def test_parse():
    word = (await Word.parse('foo')).obj
    assert word
    assert word.value == 'foo'
    
async def test_match():
    p = Pattern('foo $bar:Word baz')
    assert p
    
    m = await p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == Word('qwerty')
    
    m = await p.match('foo lorem ipsum dolor sit amet baz')
    assert not m
    
async def test_formatted():
    string = (await Word.parse('foo')).obj
    assert str(string) == '<Word value: "foo">'
    assert f'{string}' == 'foo'
