from stark.general.strings.find_substring_in_words import find_substring_in_words, endswith_startof

# test endswith_startof

def test_endswith_startof_empty_strings():
    assert endswith_startof('', '') == ''
    
def test_endswith_startof_same_strings():
    assert endswith_startof('hello', 'hello') == 'hello'
    
def test_endswith_startof_different_strings():
    assert endswith_startof('hello', 'world') == ''
    
def test_endswith_startof_partial_match_in_starts():
    assert endswith_startof('hello', 'help') == ''
    
def test_endswith_startof_partial_match_in_ends():
    assert endswith_startof('hello', 'fello') == ''
    
def test_endswith_startof_partial_match():
    assert endswith_startof('loremipsum', 'ipsumdolor') == 'ipsum'
    
def test_endswith_startof_partial_match_reversed():
    assert endswith_startof('ipsumdolor', 'loremipsum') == 'lor'
    
def test_endswith_startof_partial_match_2():
    assert endswith_startof('Sayhel', 'hello new world') == 'hel'

# test find_substring_in_words

def test_find_substring_in_words_empty_string():
    assert find_substring_in_words('', ['']) == [[0]]

def test_find_substring_in_words_empty_list():
    assert find_substring_in_words('test', []) == []

def test_find_substring_in_words_no_match():
    assert find_substring_in_words('test', ['hello', 'world']) == []

def test_find_substring_in_words_match_at_start():
    assert find_substring_in_words('hello', ['hello', 'world']) == [[0]]

def test_find_substring_in_words_match_at_end():
    assert find_substring_in_words('world', ['hello', 'world']) == [[1]]

def test_find_substring_in_words_match_in_middle():
    assert find_substring_in_words('llo', ['hello', 'world']) == [[0]]

def test_find_substring_in_words_match_partial_overlap():
    assert find_substring_in_words('ell', ['hello', 'yellow']) == [[0], [1]]

def test_find_substring_in_words_match_partial_overlap_multiple2():
    assert find_substring_in_words('ll', ['hello', 'world', 'yellow']) == [[0], [2]]

def test_find_substring_in_words_match_two_words():
    assert find_substring_in_words('hello world', ['hello', 'world']) == [[0, 1]]
    
def test_test_find_substring_in_words_match_words_with_middle_bounds():
    assert find_substring_in_words('hello new world', 'Test Sayhel lo new worldy end'.split()) == [[1, 2, 3, 4]]
