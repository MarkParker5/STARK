from stark.core import Pattern
from stark.core.patterns import expressions
from stark.general.localisation import Localizer


word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'

async def test_leading_star(get_transcription):
    p = Pattern('*text')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'{word}text'
    assert await p.match(get_transcription('text'), Localizer())
    assert await p.match(get_transcription('aaatext'), Localizer())
    assert (await p.match(get_transcription('bbb aaaatext cccc'), Localizer()))[0].subtrack.text == 'aaaatext'
    assert not await p.match(get_transcription('aaaaext'), Localizer())
    
    p = Pattern('Some *text here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'Some {word}text here'
    assert await p.match(get_transcription('Some text here'), Localizer())
    assert await p.match(get_transcription('Some aaatext here'), Localizer())
    assert (await p.match(get_transcription('bbb Some aaatext here cccc'), Localizer()))[0].subtrack.text == 'Some aaatext here'
    assert not await p.match(get_transcription('Some aaatext'), Localizer())
    
async def test_trailing_star(get_transcription):
    p = Pattern('text*')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'text{word}'
    assert await p.match(get_transcription('text'), Localizer())
    assert await p.match(get_transcription('textaaa'), Localizer())
    assert (await p.match(get_transcription('bbb textaaa cccc'), Localizer()))[0].subtrack.text == 'textaaa'
    
    p = Pattern('Some text* here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'Some text{word} here'
    assert await p.match(get_transcription('Some text here'), Localizer())
    assert await p.match(get_transcription('Some textaaa here'), Localizer())
    assert (await p.match(get_transcription('bbb Some textaaa here cccc'), Localizer()))[0].subtrack.text == 'Some textaaa here'
    assert not await p.match(get_transcription('Some textaaa '), Localizer())
    
async def test_middle_star(get_transcription):
    p = Pattern('te*xt')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'te{word}xt'
    assert await p.match(get_transcription('text'), Localizer())
    assert await p.match(get_transcription('teaaaaaxt'), Localizer())
    assert (await p.match(get_transcription('bbb teaaaaaxt cccc'), Localizer()))[0].subtrack.text == 'teaaaaaxt'
    
    p = Pattern('Some te*xt here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'Some te{word}xt here'
    assert await p.match(get_transcription('Some text here'), Localizer())
    assert await p.match(get_transcription('Some teaaaaaxt here'), Localizer())
    assert (await p.match(get_transcription('bbb Some teaaeaaaxt here cccc'), Localizer()))[0].subtrack.text == 'Some teaaeaaaxt here'
    assert not await p.match(get_transcription('Some teaaaaaxt'), Localizer())
    
async def test_double_star(get_transcription):
    p = Pattern('**')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'{words}'
    assert (await p.match(get_transcription('bbb teaaaaaxt cccc'), Localizer()))[0].subtrack.text == 'bbb teaaaaaxt cccc'
    
    p = Pattern('Some ** here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == fr'Some {words} here'
    assert await p.match(get_transcription('Some text here'), Localizer())
    assert await p.match(get_transcription('Some lorem ipsum dolor here'), Localizer())
    assert (await p.match(get_transcription('bbb Some lorem ipsum dolor here cccc'), Localizer()))[0].subtrack.text == 'Some lorem ipsum dolor here'
    
async def test_one_of(get_transcription):
    p = Pattern('(foo|bar)')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'(?:foo|bar)'
    assert await p.match(get_transcription('foo'), Localizer())
    assert await p.match(get_transcription('bar'), Localizer())
    assert (await p.match(get_transcription('bbb foo cccc'), Localizer()))[0].subtrack.text == 'foo'
    assert (await p.match(get_transcription('bbb bar cccc'), Localizer()))[0].subtrack.text == 'bar'
    
    p = Pattern('Some (foo|bar) here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'Some (?:foo|bar) here'
    assert await p.match(get_transcription('Some foo here'), Localizer())
    assert await p.match(get_transcription('Some bar here'), Localizer())
    assert (await p.match(get_transcription('bbb Some foo here cccc'), Localizer()))[0].subtrack.text == 'Some foo here'
    assert (await p.match(get_transcription('bbb Some bar here cccc'), Localizer()))[0].subtrack.text == 'Some bar here'
    assert not await p.match(get_transcription('Some foo'), Localizer())
    
async def test_optional_one_of(get_transcription):
    p = Pattern('(foo|bar)?')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'(?:foo|bar)?'
    assert await p.match(get_transcription('foo'), Localizer())
    assert await p.match(get_transcription('bar'), Localizer())
    assert not await p.match(get_transcription(''), Localizer())
    assert not await p.match(get_transcription('bbb cccc'), Localizer())
    assert (await p.match(get_transcription('bbb foo cccc'), Localizer()))[0].subtrack.text == 'foo'
    assert (await p.match(get_transcription('bbb bar cccc'), Localizer()))[0].subtrack.text == 'bar'
    
    p = Pattern('Some (foo|bar)? here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'Some (?:foo|bar)? here'
    assert await p.match(get_transcription('Some foo here'), Localizer())
    assert await p.match(get_transcription('Some bar here'), Localizer())
    assert await p.match(get_transcription('Some  here'), Localizer())
    assert (await p.match(get_transcription('bbb Some foo here cccc'), Localizer()))[0].subtrack.text == 'Some foo here'
    assert (await p.match(get_transcription('bbb Some bar here cccc'), Localizer()))[0].subtrack.text == 'Some bar here'
    assert (await p.match(get_transcription('bbb Some  here cccc'), Localizer()))[0].subtrack.text == 'Some here'
    
    # assert Pattern('[foo|bar]').compiled == Pattern('(foo|bar)?').compiled
    
async def test_one_or_more_of(get_transcription):
    p = Pattern('{foo|bar}')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'(?:(?:foo|bar)\s?)+'
    assert await p.match(get_transcription('foo'), Localizer())
    assert await p.match(get_transcription('bar'), Localizer())
    assert not await p.match(get_transcription(''), Localizer())
    assert (await p.match(get_transcription('bbb foo cccc'), Localizer()))[0].subtrack.text == 'foo'
    assert (await p.match(get_transcription('bbb bar cccc'), Localizer()))[0].subtrack.text == 'bar'
    assert (await p.match(get_transcription('bbb foo bar cccc'), Localizer()))[0].subtrack.text == 'foo bar'
    assert not await p.match(get_transcription('bbb cccc'), Localizer())
    
    p = Pattern('Some {foo|bar} here')
    p.get_compiled('en', Localizer())
    # assert p._compiled['en'] == r'Some (?:(?:foo|bar)\s?)+ here'
    assert await p.match(get_transcription('Some foo here'), Localizer())
    assert await p.match(get_transcription('Some bar here'), Localizer())
    assert not await p.match(get_transcription('Some  here'), Localizer())
    assert (await p.match(get_transcription('bbb Some foo here cccc'), Localizer()))[0].subtrack.text == 'Some foo here'
    assert (await p.match(get_transcription('bbb Some bar here cccc'), Localizer()))[0].subtrack.text == 'Some bar here'
    assert (await p.match(get_transcription('bbb Some foo bar here cccc'), Localizer()))[0].subtrack.text == 'Some foo bar here'
    assert not await p.match(get_transcription('Some foo'), Localizer())
