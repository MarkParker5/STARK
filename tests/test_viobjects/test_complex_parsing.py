
import pytest 
from VICore import Pattern, VIObject, ParseError
from VICore.VIObjects.VIObject import classproperty


class VILorem(VIObject):
    
    @classproperty
    def pattern(cls):
        return Pattern('* ipsum')
    
    def did_parse(self, from_string: str) -> str:
        if 'lorem' not in from_string:
            raise ParseError('lorem not found')
        self.value = 'lorem'
        return 'lorem'
    
def test_complex_parsing_failed():
    with pytest.raises(ParseError):
        VILorem.parse('some lor ipsum')
    
def test_complex_parsing():
    string = 'some lorem ipsum'
    match = VILorem.parse(string)
    assert match
    assert match.obj
    assert match.obj.value == 'lorem'
    assert match.substring == 'lorem'
    assert VILorem.pattern.match(string)[0].substring == 'lorem ipsum'