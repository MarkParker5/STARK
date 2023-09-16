
import pytest 
from core import Pattern, Object, ParseError
from general.classproperty import classproperty


class Lorem(Object):
    
    @classproperty
    def pattern(cls):
        return Pattern('* ipsum')
    
    async def did_parse(self, from_string: str) -> str:
        if 'lorem' not in from_string:
            raise ParseError('lorem not found')
        self.value = 'lorem'
        return 'lorem'
    
async def test_complex_parsing_failed():
    with pytest.raises(ParseError):
        await Lorem.parse('some lor ipsum')
    
async def test_complex_parsing():
    string = 'some lorem ipsum'
    match = await Lorem.parse(string)
    assert match
    assert match.obj
    assert match.obj.value == 'lorem'
    assert match.substring == 'lorem'
    assert (await Lorem.pattern.match(string))[0].substring == 'lorem ipsum'
    