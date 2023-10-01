from stark.general.strings.levenshtein import levenshtein

def test_levenshtein_empty_query():
    assert set(levenshtein('', 'hello', 0.5)) == set()

def test_levenshtein_empty_string():
    assert set(levenshtein('hello', '', 0.5)) == set()

def test_levenshtein_exact_match():
    assert set(levenshtein('hello', 'hello', 0.5)) == {'hello'}
    
def test_levenshtein_no_match():
    assert set(levenshtein('hello', 'world', 0.5)) == set()
    
def test_zero_threshold():
    assert set(levenshtein('hello', 'world', 0)) == set()
    
def test_one_threshold():
    assert set(levenshtein('hello', 'world', 1)) == {'world'}
    
def test_levenshtein_substring_with_query_spaces_match():
     # can be done by removing spaces from query that leads to easy `test_levenshtein_substring_match`
    assert set(levenshtein('ln kn pk', 'lorem ispum lnknpk sit amet', 0)) == {'lnknpk'}
    
def test_levenshtein_substring_both_with_spaces_match():
     # can be done by removing spaces from query that leads to the `test_levenshtein_substring_with_spaces_match`
    assert set(levenshtein('ln kn pk', 'lorem ispum ln kn pk sit amet', 0)) == {'ln kn pk'}
    
def test_levenshtein_substring_match():
     # easy case
    assert set(levenshtein('lnknpk', 'lorem ispum lnknpk sit amet', 0)) == {'lnknpk'}

def test_levenshtein_substring_with_spaces_match():
    # the most important and difficult case
    assert set(levenshtein('lnknpk', 'lorem ispum ln kn pk sit amet', 0)) == {'ln kn pk'}

def test_multiple_levenshtein_substring_with_spaces_match():
    # the very most important and difficult case
    assert set(levenshtein('lnknpk', 'lorem ispum ln kn pk sit amet lnk npk foo bar baz', 0)) == {'ln kn pk', 'lnk npk'}
