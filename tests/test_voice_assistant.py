from datetime import datetime, timedelta
from VoiceAssistant import Mode


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

def test_background_command_with_waiting_mode(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background min')
    
    # start background task
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force a timeout
    voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
    
    # check finished background task
    voice_assistant.commands_context._check_threads()
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
    # check saved response
    assert len(voice_assistant._responses) == 1
    
    # emulate delay after last response before repeating
    voice_assistant._responses[0].time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
    
    # interact to reset timeout mode and repeat saved response
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'   
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'

def test_background_command_with_inactive_mode(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background min')
    
    # start background task
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
    assert len(voice_assistant.commands_context._threads) == 1
    
    # set inactive mode
    voice_assistant.mode = Mode.inactive
    
    # check finished background task
    voice_assistant.commands_context._check_threads()
    assert len(voice_assistant.speech_synthesizer.results) == 0
    
    # check saved response
    assert len(voice_assistant._responses) == 1
    
    # interact to reset timeout mode and repeat saved response
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'   
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
def test_background_waiting_needs_input(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background needs input')
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force a timeout
    voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
    
    # wait for thread to finish
    voice_assistant.commands_context._threads[0].thread.join()
    
    # receive context output
    voice_assistant.commands_context._check_threads()
    
    # voice assistant should save all responses for later
    assert len(voice_assistant._responses) == 8
    assert len(voice_assistant.speech_synthesizer.results) == 8
    voice_assistant.speech_synthesizer.results.clear()
    
    # emulate delay after last response before repeating
    for response in voice_assistant._responses:
        response.time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
    
    # interact to reset timeout mode
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    
    # voice assistant should say all responses until needs input
    assert len(voice_assistant.speech_synthesizer.results) == 5
    assert len(voice_assistant._responses) == 4
    
    for response in ['Hello, world!', 'First response', 'Second response', 'Third response', 'Needs input']:
        assert voice_assistant.speech_synthesizer.results.pop(0).text == response
    
    # interact to emulate user input and continue repeating responses
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    
    # voice assistant should say all left responses
    assert len(voice_assistant.speech_synthesizer.results) == 5
    assert len(voice_assistant._responses) == 0
    for response in ['Hello, world!', 'Fourth response', 'Fifth response', 'Sixth response', 'Finished long background task']:
        assert voice_assistant.speech_synthesizer.results.pop(0).text == response
    
def test_background_waiting_with_context(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background with context')
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force a timeout
    voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
    
    # wait for thread to finish
    voice_assistant.commands_context._threads[0].thread.join()
    
    # receive context output
    voice_assistant.commands_context._check_threads()
    
    # voice assistant should play all (including adding context) and save all responses for later
    assert len(voice_assistant.speech_synthesizer.results) == 2 # 2 = first and returned
    assert len(voice_assistant._responses) == 1 # first response is not saved because it plays immediately
    assert len(voice_assistant.commands_context._context_queue) == 2
    voice_assistant.speech_synthesizer.results.clear()
    
    # emulate delay after last response before repeating
    for response in voice_assistant._responses:
        response.time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
    
    # interact to reset timeout mode, voice assistant should reset context, repeat responses and add response context
    voice_assistant.speech_recognizer_did_receive_final_result('lorem ipsum dolor')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert len(voice_assistant.commands_context._context_queue) == 2

def test_background_waiting_remove_response(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background remove response')
    assert len(voice_assistant.commands_context._threads) == 1
    voice_assistant.speech_synthesizer.results.clear()
    
    # force a timeout by settings zero time
    voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
    
    # catch all responses
    responses_cache = voice_assistant._responses.copy()
    
    while voice_assistant.commands_context._threads[0].thread.is_alive():
        for response in voice_assistant._responses:
            if not response in responses_cache:
                responses_cache.append(response)
    
    # check response cached, removed and will not be repeated
    assert len(responses_cache) == 1
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert responses_cache.pop(0).text == 'Deleted response'
    assert len(voice_assistant._responses) == 0
    voice_assistant.speech_synthesizer.results.clear()
    
    # interact to reset timeout mode, check that removed response is not repeated
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'