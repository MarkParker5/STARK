from stark.general.strings.find_substring_in_words import find_substring_in_words, startswith_endof

def test_startswith_endof_empty_strings():
    assert startswith_endof('', '') == ''
    
def test_startswith_endof_same_strings():
    assert startswith_endof('hello', 'hello') == 'hello'
    
def test_startswith_endof_different_strings():
    assert startswith_endof('hello', 'world') == ''
    
def test_startswith_endof_partial_match_in_starts():
    assert startswith_endof('hello', 'help') == ''
    
def test_startswith_endof_partial_match_in_ends():
    assert startswith_endof('hello', 'fello') == ''
    
def test_startswith_endof_partial_match():
    assert startswith_endof('loremipsum', 'ipsumdolor') == 'ipsum'
    
def test_startswith_endof_partial_match_reversed():
    assert startswith_endof('ipsumdolor', 'loremipsum') == 'lor'

def test_find_substring_in_words():
    ...
