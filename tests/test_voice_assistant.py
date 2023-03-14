from datetime import datetime


def test_background_command(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background min')
    
    # start background task
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
    assert len(voice_assistant.commands_context._threads) == 1
    
    # check finished background task
    voice_assistant.commands_context._check_threads()
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
    # check saved response
    assert len(voice_assistant._responses) == 0

def test_background_command_with_inactive_mode(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background min')
    
    # start background task
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force inactive mode by settings zero time
    voice_assistant._last_interaction_time = datetime.fromtimestamp(0)
    
    # check finished background task
    voice_assistant.commands_context._check_threads()
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
    # check saved response
    assert len(voice_assistant._responses) == 1
    
    # interact to disable inactive mode and repeat saved response
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'   
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'

def test_background_command_with_afk_mode():
    pass

def test_background_command_with_afk_mode_and_inactive_mode():
    pass