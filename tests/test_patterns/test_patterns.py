from core import Pattern
from core.patterns import expressions


word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'

async def test_leading_star():
    p = Pattern('*text')
    assert p.compiled == fr'{word}text'
    assert await p.match('text')
    assert await p.match('aaatext')
    assert (await p.match('bbb aaaatext cccc'))[0].substring == 'aaaatext'
    assert not await p.match('aaaaext')
    
    p = Pattern('Some *text here')
    assert p.compiled == fr'Some {word}text here'
    assert await p.match('Some text here')
    assert await p.match('Some aaatext here')
    assert (await p.match('bbb Some aaatext here cccc'))[0].substring == 'Some aaatext here'
    assert not await p.match('aaatext here')
    
async def test_trailing_star():
    p = Pattern('text*')
    assert p.compiled == fr'text{word}'
    assert await p.match('text')
    assert await p.match('textaaa')
    assert (await p.match('bbb textaaa cccc'))[0].substring == 'textaaa'
    
    p = Pattern('Some text* here')
    assert p.compiled == fr'Some text{word} here'
    assert await p.match('Some text here')
    assert await p.match('Some textaaa here')
    assert (await p.match('bbb Some textaaa here cccc'))[0].substring == 'Some textaaa here'
    assert not await p.match('Some textaaa ')

async def test_middle_star():
    p = Pattern('te*xt')
    assert p.compiled == fr'te{word}xt'
    assert await p.match('text')
    assert await p.match('teaaaaaxt')
    assert (await p.match('bbb teaaaaaxt cccc'))[0].substring == 'teaaaaaxt'
    
    p = Pattern('Some te*xt here')
    assert p.compiled == fr'Some te{word}xt here'
    assert await p.match('Some text here')
    assert await p.match('Some teaaaaaxt here')
    assert (await p.match('bbb Some teaaeaaaxt here cccc'))[0].substring == 'Some teaaeaaaxt here'
    assert not await p.match('Some teaaaaaxt')
    
async def test_double_star():
    p = Pattern('**')
    assert p.compiled == fr'{words}'
    assert (await p.match('bbb teaaaaaxt cccc'))[0].substring == 'bbb teaaaaaxt cccc'
    
    p = Pattern('Some ** here')
    assert p.compiled == fr'Some {words} here'
    assert await p.match('Some text here')
    assert await p.match('Some lorem ipsum dolor here')
    assert (await p.match('bbb Some lorem ipsum dolor here cccc'))[0].substring == 'Some lorem ipsum dolor here'
    
async def test_one_of():
    p = Pattern('(foo|bar)')
    assert p.compiled == r'(?:foo|bar)'
    assert await p.match('foo')
    assert await p.match('bar')
    assert (await p.match('bbb foo cccc'))[0].substring == 'foo'
    assert (await p.match('bbb bar cccc'))[0].substring == 'bar'
    
    p = Pattern('Some (foo|bar) here')
    assert p.compiled == r'Some (?:foo|bar) here'
    assert await p.match('Some foo here')
    assert await p.match('Some bar here')
    assert (await p.match('bbb Some foo here cccc'))[0].substring == 'Some foo here'
    assert (await p.match('bbb Some bar here cccc'))[0].substring == 'Some bar here'
    assert not await p.match('Some foo')
    
async def test_optional_one_of():
    p = Pattern('(foo|bar)?')
    assert p.compiled == r'(?:foo|bar)?'
    assert await p.match('foo')
    assert await p.match('bar')
    assert not await p.match('')
    assert not await p.match('bbb cccc')
    assert (await p.match('bbb foo cccc'))[0].substring == 'foo'
    assert (await p.match('bbb bar cccc'))[0].substring == 'bar'
    
    p = Pattern('Some (foo|bar)? here')
    assert p.compiled == r'Some (?:foo|bar)? here'
    assert await p.match('Some foo here')
    assert await p.match('Some bar here')
    assert await p.match('Some  here')
    assert (await p.match('bbb Some foo here cccc'))[0].substring == 'Some foo here'
    assert (await p.match('bbb Some bar here cccc'))[0].substring == 'Some bar here'
    assert (await p.match('bbb Some  here cccc'))[0].substring == 'Some  here'
    
    # assert Pattern('[foo|bar]').compiled == Pattern('(foo|bar)?').compiled
    
async def test_one_or_more_of():
    p = Pattern('{foo|bar}')
    assert p.compiled == r'(?:(?:foo|bar)\s?)+'
    assert await p.match('foo')
    assert await p.match('bar')
    assert not await p.match('')
    assert (await p.match('bbb foo cccc'))[0].substring == 'foo'
    assert (await p.match('bbb bar cccc'))[0].substring == 'bar'
    assert (await p.match('bbb foo bar cccc'))[0].substring == 'foo bar'
    assert not await p.match('bbb cccc')
    
    p = Pattern('Some {foo|bar} here')
    assert p.compiled == r'Some (?:(?:foo|bar)\s?)+ here'
    assert await p.match('Some foo here')
    assert await p.match('Some bar here')
    assert not await p.match('Some  here')
    assert (await p.match('bbb Some foo here cccc'))[0].substring == 'Some foo here'
    assert (await p.match('bbb Some bar here cccc'))[0].substring == 'Some bar here'
    assert (await p.match('bbb Some foo bar here cccc'))[0].substring == 'Some foo bar here'
    assert not await p.match('Some foo')
