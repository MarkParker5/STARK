from stark.general.suggestions import SuggestionsManager
from stark.models.transcription import Transcription, TranscriptionTrack, TranscriptionWord

def test_add_keyword():
    manager = SuggestionsManager()
    manager.add_keyword('hello')
    assert len(manager.keywords) == 1
    assert 'hello' in manager.keywords
    assert len(manager.keywords['hello']) == 1
    assert 'hello' in manager.keywords['hello']
    
    manager.add_keyword('hello', 'hi')
    assert len(manager.keywords) == 1
    assert 'hello' in manager.keywords
    assert len(manager.keywords['hello']) == 2
    assert 'hello' in manager.keywords['hello']
    assert 'hi' in manager.keywords['hello']
    
    manager.add_keyword('hello', 'hi')
    assert len(manager.keywords) == 1
    assert 'hello' in manager.keywords
    assert len(manager.keywords['hello']) == 2
    assert 'hello' in manager.keywords['hello']
    assert 'hi' in manager.keywords['hello']

def test_add_transcription_suggestions():
    manager = SuggestionsManager()
    track = TranscriptionTrack(
        text = 'hello world',
        result = [
            TranscriptionWord(word = 'hello', start = 0.0, end = 1.0, conf = 1.0),
            TranscriptionWord(word = 'world', start = 1.0, end = 2.0, conf = 1.0)
        ],
        language_code = 'en'
    )
    transcription = Transcription(
        best = track,
        origins = {'en': track}
    )
    manager.add_keyword('hello')
    manager.add_transcription_suggestions(transcription)
    assert set(transcription.suggestions) == {('hello', 'hello')}

def test_get_string_suggestions():
    manager = SuggestionsManager()
    manager.add_keyword('hello')
    manager.add_keyword('world')
    
    suggestions = manager.get_string_suggestions('hello world', 'en')
    assert suggestions == {('hello', 'hello'), ('world', 'world')}
    
    suggestions = manager.get_string_suggestions('hilo wart', 'en')
    assert suggestions == {('hilo', 'hello'), ('wart', 'world')}

def test_get_string_suggestions_advanced():
    manager = SuggestionsManager()
    for word in ['spotify', 'telegram', 'instagram', 'led zeppelin', 'imagine dragons', 'highway to hell', 'linkin park']:
        manager.add_keyword(word, language_code = 'en', multilingual = True)
        
    assert manager.get_string_suggestions('телеграм', 'ru') == {('телеграм', 'telegram')}
    assert manager.get_string_suggestions('ледзеплин', 'ru') == {('ледзеплин', 'led zeppelin')}
    assert manager.get_string_suggestions('имя джин драгонс', 'ru') == {('имя джин драгонс', 'imagine dragons')}
    assert manager.get_string_suggestions('хайвей та хел', 'ru') == {('хайвей та хел', 'highway to hell')}
    assert manager.get_string_suggestions('линкольн парк', 'ru') == {('линкольн парк', 'linkin park')}
    assert manager.get_string_suggestions('спу ти фай', 'ru') == {('спу ти фай', 'spotify')}
