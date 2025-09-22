import pytest

from stark.core import Pattern
from stark.core.patterns import rules

word = fr'[{rules.alphanumerics}]*'
words = fr'[{rules.alphanumerics}\s]+'
words_optional = fr'[{rules.alphanumerics}\s]*'

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

async def test_single_star():
    p = Pattern('Some * here')
    assert p.compiled == fr'Some {word} here'
    assert (await p.match('bbb Some teaaeaaaxt here cccc'))[0].substring == 'Some teaaeaaaxt here'
    assert await p.match('Some  here') # note double space

    p = Pattern('Some *')
    assert p.compiled == fr'Some {word}'
    assert (await p.match('bbb Some teaaeaaaxt here cccc'))[0].substring == 'Some teaaeaaaxt'
    assert await p.match('Some ') # note space

    p = Pattern('* some')
    assert p.compiled == fr'{word} some'
    assert (await p.match('bbb teaaeaaaxt some cccc'))[0].substring == 'teaaeaaaxt some'
    assert await p.match(' some') # note space

    p = Pattern('*')
    assert p.compiled == fr'{word}'
    # assert (await p.match('bbb teaaeaaaxt some cccc'))[0].substring == 'bbb' # takes the first word
    assert (await p.match('bbb teaaeaaaxt some cccc'))[0].substring == 'teaaeaaaxt' # takes the largest word, TODO: review behavior
    assert not await p.match('')
    assert not await p.match(' ')
    assert len(await p.match('a b c d')) == 4, await p.match('a b c d')

async def test_double_star():
    p = Pattern('**')
    assert p.compiled == fr'{words}'
    assert (await p.match('bbb teaaaaaxt cccc'))[0].substring == 'bbb teaaaaaxt cccc'

    p = Pattern('Some ** here')
    assert p.compiled == fr'Some {words} here'
    assert await p.match('Some text here')
    assert await p.match('Some lorem ipsum dolor here')
    assert (await p.match('bbb Some lorem ipsum dolor here cccc'))[0].substring == 'Some lorem ipsum dolor here'
    assert not await p.match('some here')

async def test_optional_double_star():
    p = Pattern('**?')
    assert p.compiled == fr'{words_optional}'
    assert (await p.match('bbb teaaaaaxt cccc'))[0].substring == 'bbb teaaaaaxt cccc'

    p = Pattern('Some **?here')
    assert p.compiled == fr'Some {words_optional}here'
    assert await p.match('Some text here')
    assert await p.match('Some lorem ipsum dolor here')
    assert (await p.match('bbb Some lorem ipsum dolor here cccc'))[0].substring == 'Some lorem ipsum dolor here'
    assert await p.match('Some here') # The only difference from double star

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

@pytest.mark.skip(reason="Not implemented as a not important feature")
async def test_one_of_with_spaces():
    p = Pattern('Hello ( foo | bar | baz ) world')
    print(p.compiled)
    assert await p.match('Hello foo world')
    assert await p.match('Hello bar world')
    assert await p.match('Hello baz world')

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

async def test_none_or_more_of():
    p = Pattern('one {foo|bar}?two')
    assert p.compiled == r'one (?:(?:foo|bar)\s?)*two'
    assert await p.match('one two')
    assert await p.match('one foo two')
    assert await p.match('one bar two')
    assert await p.match('one foo bar two')
    assert not await p.match('one foo bar baz two')
    assert (await p.match('bbb one two cccc'))[0].substring == 'one two'
    assert (await p.match('bbb one foo two cccc'))[0].substring == 'one foo two'
    assert (await p.match('bbb one bar two cccc'))[0].substring == 'one bar two'
    assert (await p.match('bbb one foo bar two cccc'))[0].substring == 'one foo bar two'
