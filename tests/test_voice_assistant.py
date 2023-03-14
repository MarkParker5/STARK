import time
from datetime import datetime
import config


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

def test_background_command_with_afk_mode(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background min')
    
    # start background task
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force afk mode
    config.is_afk = True
    
    # check finished background task
    voice_assistant.commands_context._check_threads()
    assert len(voice_assistant.speech_synthesizer.results) == 0
    
    # check saved response
    assert len(voice_assistant._responses) == 1
    
    # interact to disable inactive mode and repeat saved response
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'   
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
def test_background_inactive_needs_input(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background needs input')
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force inactive mode by settings zero time
    voice_assistant._last_interaction_time = datetime.fromtimestamp(0)
    
    # wait for thread to finish
    voice_assistant.commands_context._threads[0].thread.join()
    
    # receive context output
    voice_assistant.commands_context._check_threads()
    
    # voice assistant should save all responses for later
    assert len(voice_assistant._responses) == 8
    assert len(voice_assistant.speech_synthesizer.results) == 8
    voice_assistant.speech_synthesizer.results.clear()
    
    # interact to disable inactive mode
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
    
def test_background_inactive_with_context(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background with context')
    assert len(voice_assistant.commands_context._threads) == 1
    
    # force inactive mode by settings zero time
    voice_assistant._last_interaction_time = datetime.fromtimestamp(0)
    
    # wait for thread to finish
    voice_assistant.commands_context._threads[0].thread.join()
    
    # receive context output
    voice_assistant.commands_context._check_threads()
    
    # voice assistant should play all (including adding context) and save all responses for later
    assert len(voice_assistant.speech_synthesizer.results) == 2 # 2 = first and returned
    assert len(voice_assistant._responses) == 1 # first response is not saved because it plays immediately
    assert len(voice_assistant.commands_context._context_queue) == 2
    voice_assistant.speech_synthesizer.results.clear()
    
    # interact to disable inactive mode, voice assistant should reset context, repeat responses and add response context
    voice_assistant.speech_recognizer_did_receive_final_result('lorem ipsum dolor')
    assert len(voice_assistant.speech_synthesizer.results) == 2
    assert len(voice_assistant.commands_context._context_queue) == 2

def test_background_inactive_remove_response(voice_assistant):
    voice_assistant.speech_recognizer_did_receive_final_result('background remove response')
    assert len(voice_assistant.commands_context._threads) == 1
    voice_assistant.speech_synthesizer.results.clear()
    
    # force inactive mode by settings zero time
    voice_assistant._last_interaction_time = datetime.fromtimestamp(0)
    
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
    
    # interact to disable inactive mode, check that removed response is not repeated
    voice_assistant.speech_recognizer_did_receive_final_result('hello world')
    assert len(voice_assistant.speech_synthesizer.results) == 1
    assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Hello, world!'