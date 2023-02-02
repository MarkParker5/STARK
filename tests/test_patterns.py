import re
from VICore import Pattern
from VICore.patterns import expressions

word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'

def test_leading_star():
    p = Pattern('*text')
    assert p.compiled == fr'{word}text'
    assert p.match('text')
    assert p.match('aaatext')
    assert p.match('bbb aaaatext cccc').substring == 'aaaatext'
    assert not p.match('aaaaext')
    
    p = Pattern('Some *text here')
    assert p.compiled == fr'Some {word}text here'
    assert p.match('Some text here')
    assert p.match('Some aaatext here')
    assert p.match('bbb Some aaatext here cccc').substring == 'Some aaatext here'
    assert not p.match('aaatext here')
    
def test_trailing_star():
    p = Pattern('text*')
    assert p.compiled == fr'text{word}'
    assert p.match('text')
    assert p.match('textaaa')
    assert p.match('bbb textaaa cccc').substring == 'textaaa'
    
    p = Pattern('Some text* here')
    assert p.compiled == fr'Some text{word} here'
    assert p.match('Some text here')
    assert p.match('Some textaaa here')
    assert p.match('bbb Some textaaa here cccc').substring == 'Some textaaa here'
    assert not p.match('Some textaaa ')

def test_middle_star():
    p = Pattern('te*xt')
    assert p.compiled == fr'te{word}xt'
    assert p.match('text')
    assert p.match('teaaaaaxt')
    assert p.match('bbb teaaaaaxt cccc').substring == 'teaaaaaxt'
    
    p = Pattern('Some te*xt here')
    assert p.compiled == fr'Some te{word}xt here'
    assert p.match('Some text here')
    assert p.match('Some teaaaaaxt here')
    assert p.match('bbb Some teaaeaaaxt here cccc').substring == 'Some teaaeaaaxt here'
    assert not p.match('Some teaaaaaxt')
    
def test_double_star():
    p = Pattern('**')
    assert p.compiled == fr'{words}'
    assert p.match('bbb teaaaaaxt cccc').substring == 'bbb teaaaaaxt cccc'
    
    p = Pattern('Some ** here')
    assert p.compiled == fr'Some {words} here'
    assert p.match('Some text here')
    assert p.match('Some lorem ipsum dolor here')
    assert p.match('bbb Some lorem ipsum dolor here cccc').substring == 'Some lorem ipsum dolor here'
    
def test_one_of():
    p = Pattern('(foo|bar)')
    assert p.compiled == r'(?:foo|bar)'
    assert p.match('foo')
    assert p.match('bar')
    assert p.match('bbb foo cccc').substring == 'foo'
    assert p.match('bbb bar cccc').substring == 'bar'
    
    p = Pattern('Some (foo|bar) here')
    assert p.compiled == r'Some (?:foo|bar) here'
    assert p.match('Some foo here')
    assert p.match('Some bar here')
    assert p.match('bbb Some foo here cccc').substring == 'Some foo here'
    assert p.match('bbb Some bar here cccc').substring == 'Some bar here'
    assert not p.match('Some foo')
    
def test_optional_one_of():
    p = Pattern('(foo|bar)?')
    assert p.compiled == r'(?:foo|bar)?'
    assert p.match('foo')
    assert p.match('bar')
    assert p.match('')
    assert p.match('bbb foo cccc').substring == 'foo'
    assert p.match('bbb bar cccc').substring == 'bar'
    assert p.match('bbb cccc').substring == ''
    
    p = Pattern('Some (foo|bar)? here')
    assert p.compiled == r'Some (?:foo|bar)? here'
    assert p.match('Some foo here')
    assert p.match('Some bar here')
    assert p.match('Some  here')
    assert p.match('bbb Some foo here cccc').substring == 'Some foo here'
    assert p.match('bbb Some bar here cccc').substring == 'Some bar here'
    assert p.match('bbb Some  here cccc').substring == 'Some  here'
    
    # assert Pattern('[foo|bar]').compiled == Pattern('(foo|bar)?').compiled
    
def test_one_or_more_of():
    p = Pattern('{foo|bar}')
    assert p.compiled == r'(?:(?:foo|bar)\s?)+'
    assert p.match('foo')
    assert p.match('bar')
    assert not p.match('')
    assert p.match('bbb foo cccc').substring == 'foo'
    assert p.match('bbb bar cccc').substring == 'bar'
    assert p.match('bbb foo bar cccc').substring == 'foo bar'
    assert not p.match('bbb cccc')
    
    p = Pattern('Some {foo|bar} here')
    assert p.compiled == r'Some (?:(?:foo|bar)\s?)+ here'
    assert p.match('Some foo here')
    assert p.match('Some bar here')
    assert not p.match('Some  here')
    assert p.match('bbb Some foo here cccc').substring == 'Some foo here'
    assert p.match('bbb Some bar here cccc').substring == 'Some bar here'
    assert p.match('bbb Some foo bar here cccc').substring == 'Some foo bar here'
    assert not p.match('Some foo')
    
def test_typed_arguments():
    p = Pattern('lorem $name:VIWord dolor')
    assert p.compiled == fr'lorem (?P<name>{word}) dolor'
    
    m = p.match('lorem ipsum dolor')
    assert m
    assert m.substring == 'lorem ipsum dolor'
    assert m.groups == {'name': 'ipsum'}
    assert not p.match('lorem ipsum foo dolor')
    
    p = Pattern('lorem $name:VIString dolor')
    m = p.match('lorem ipsum foo bar dolor')
    assert m
    assert m.substring == 'lorem ipsum foo bar dolor'
    assert m.groups == {'name': 'ipsum foo bar'}