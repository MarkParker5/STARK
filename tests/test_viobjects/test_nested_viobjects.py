from VICore import VIObject, VIWord, Pattern
from VICore.VIObjects.VIObject import classproperty


class VITwoWords(VIObject):
    
    word1: VIWord
    word2: VIWord

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:VIWord $word2:VIWord')

Pattern.argumentTypes['VITwoWords'] = VITwoWords

def test_nested_viobjects():
    p = Pattern('$words:VITwoWords')
    assert p
    assert p.compiled
    
    m = p.match('foo bar')
    assert m