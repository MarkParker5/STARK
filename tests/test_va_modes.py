import pytest
import anyio
from datetime import timedelta
from stark.voice_assistant import Mode


async def test_background_command_with_waiting_mode(voice_assistant, autojump_clock):
    async with voice_assistant() as voice_assistant:
        await voice_assistant.speech_recognizer_did_receive_final_result('background min')
        
        await anyio.sleep(0.2) # allow to capture first command response
        
        # start background task
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
        
        # force a timeout
        voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
        
        # wait for command to finish
        await anyio.sleep(1)
        
        # check finished background command
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
        
        # check saved response
        assert len(voice_assistant._responses) == 1
        
        # emulate delay after last response before repeating
        voice_assistant._responses[0].time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
        
        # interact to reset timeout mode and repeat saved response
        await voice_assistant.speech_recognizer_did_receive_final_result('test')
        await anyio.sleep(0.2) # allow to capture command response
        assert len(voice_assistant.speech_synthesizer.results) == 2
        assert [r.text for r in voice_assistant.speech_synthesizer.results] == ['test', 'Finished background task']

async def test_background_command_with_inactive_mode(voice_assistant, autojump_clock):
    async with voice_assistant() as voice_assistant:
        await voice_assistant.speech_recognizer_did_receive_final_result('background min')
        
        await anyio.sleep(0.2) # allow to capture first command response
        
        # start background task
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Starting background task'
        
        # set inactive mode
        voice_assistant.mode = Mode.inactive
        
        # wait for command to finish
        await anyio.sleep(1)
        
        # check finished background task
        assert len(voice_assistant.speech_synthesizer.results) == 0
        
        # check saved response
        assert len(voice_assistant._responses) == 1
        
        # interact to reset timeout mode and repeat saved response
        await voice_assistant.speech_recognizer_did_receive_final_result('test')
        await anyio.sleep(0.2) # allow to capture command response
        assert len(voice_assistant.speech_synthesizer.results) == 2
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'test'   
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'Finished background task'
    
async def test_background_waiting_needs_input(voice_assistant, autojump_clock):
    async with voice_assistant() as voice_assistant:
        await voice_assistant.speech_recognizer_did_receive_final_result('background needs input')
        
        await anyio.sleep(0.2) # allow to capture first command response
        
        # force a timeout
        voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
        
        # wait for command to finish
        await anyio.sleep(1)
        
        # voice assistant should save all responses for later
        assert len(voice_assistant._responses) == 8
        assert len(voice_assistant.speech_synthesizer.results) == 8
        voice_assistant.speech_synthesizer.results.clear()
        
        # emulate delay after last response before repeating
        for response in voice_assistant._responses:
            response.time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
        
        # interact to reset timeout mode
        await voice_assistant.speech_recognizer_did_receive_final_result('test')
        
        await anyio.sleep(0.2) # allow to capture command response
        
        # voice assistant should say all responses until needs input
        assert len(voice_assistant.speech_synthesizer.results) == 5
        assert len(voice_assistant._responses) == 4
        
        for response in ['test', 'First response', 'Second response', 'Third response', 'Needs input']:
            assert voice_assistant.speech_synthesizer.results.pop(0).text == response
        
        # interact to emulate user input and continue repeating responses
        await voice_assistant.speech_recognizer_did_receive_final_result('test')
        await anyio.sleep(0.2) # allow to capture command response
        
        # voice assistant should say all left responses
        assert len(voice_assistant.speech_synthesizer.results) == 5
        assert len(voice_assistant._responses) == 0
        for response in ['test', 'Fourth response', 'Fifth response', 'Sixth response', 'Finished long background task']:
            assert voice_assistant.speech_synthesizer.results.pop(0).text == response
    
async def test_background_waiting_with_context(voice_assistant, autojump_clock):
    async with voice_assistant() as voice_assistant:
        await voice_assistant.speech_recognizer_did_receive_final_result('background with context')
        
        # force a timeout
        voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
        
        # wait for command to finish
        await anyio.sleep(2)
        
        # voice assistant should play all (including adding context) and save all responses for later
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert len(voice_assistant._responses) == 1 # first response is not saved because it plays immediately
        assert len(voice_assistant.commands_context._context_queue) == 2
        voice_assistant.speech_synthesizer.results.clear()
        
        # emulate delay after last response before repeating
        for response in voice_assistant._responses:
            response.time -= timedelta(seconds = voice_assistant.mode.timeout_before_repeat + 1)
        
        # interact to reset timeout mode, voice assistant should reset context, repeat responses and add response context
        await voice_assistant.speech_recognizer_did_receive_final_result('lorem ipsum dolor')
        await anyio.sleep(0.2) # allow to capture command response
        assert len(voice_assistant.speech_synthesizer.results) == 2
        assert len(voice_assistant.commands_context._context_queue) == 2

async def test_background_waiting_remove_response(voice_assistant, autojump_clock):
    async with voice_assistant() as voice_assistant:
        await voice_assistant.speech_recognizer_did_receive_final_result('background remove response')
        voice_assistant.speech_synthesizer.results.clear()
        
        # force a timeout by settings zero time
        voice_assistant._last_interaction_time -= timedelta(seconds = voice_assistant.mode.timeout_after_interaction + 1)
        
        await anyio.sleep(0.2) # allow to capture command response
        responses_cache = voice_assistant._responses.copy() # cache all responses
        
        # wait for command to finish (and delete first response)
        await anyio.sleep(1)
        
        # check response cached
        assert len(responses_cache) == 1
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert responses_cache.pop(0).text == 'Deleted response'
        # check voice_assistant doesn't have response
        assert len(voice_assistant._responses) == 0
        voice_assistant.speech_synthesizer.results.clear()
        
        # interact to reset timeout mode, check that removed response is not repeated
        await voice_assistant.speech_recognizer_did_receive_final_result('test')
        await anyio.sleep(1) # allow to capture command response
        assert len(voice_assistant.speech_synthesizer.results) == 1
        assert voice_assistant.speech_synthesizer.results.pop(0).text == 'test'
