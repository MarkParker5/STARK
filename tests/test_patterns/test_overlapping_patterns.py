from VICore import Pattern, VIObject, ParseError, VIWord, VIString
from VICore.patterns import expressions
from VICore.VIObjects.VIObject import classproperty


class VILorem(VIObject):
    
    @classproperty
    def pattern(cls):
        return Pattern('*')
    
    def did_parse(self, from_string: str) -> str:
        if 'lorem' not in from_string:
            raise ParseError('lorem not found')
        self.value = 'lorem'
        return 'lorem'
    
def test_complex_parsing():
    pass

def test_adjusted_start_end():
    pass

def test_overlapping_patterns():
    pass

def test_caching():
    pass
     