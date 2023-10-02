import anyio


async def test_basic_search(commands_context_flow_filled, autojump_clock, get_transcription):
    async with commands_context_flow_filled() as (context, context_delegate):
        assert len(context_delegate.responses) == 0
        assert len(context._context_queue) == 1
        
        await context.process_transcription(get_transcription('lorem ipsum dolor'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Lorem!'
        assert len(context._context_queue) == 1

async def test_second_context_layer(commands_context_flow_filled, autojump_clock, get_transcription):
    async with commands_context_flow_filled() as (context, context_delegate):
    
        await context.process_transcription(get_transcription('hello world'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Hello, world!'
        assert len(context._context_queue) == 2
        context_delegate.responses.clear()
        
        await context.process_transcription(get_transcription('hello'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Hi, world!'
        assert len(context._context_queue) == 2
        context_delegate.responses.clear()
    
async def test_context_pop_on_not_found(commands_context_flow_filled, autojump_clock, get_transcription):
    async with commands_context_flow_filled() as (context, context_delegate):
    
        await context.process_transcription(get_transcription('hello world'))
        await anyio.sleep(5)
        assert len(context._context_queue) == 2
        assert len(context_delegate.responses) == 1
        context_delegate.responses.clear()
        
        await context.process_transcription(get_transcription('lorem ipsum dolor'))
        await anyio.sleep(5)
        assert len(context._context_queue) == 1
        assert len(context_delegate.responses) == 1

async def test_context_pop_context_response_action(commands_context_flow_filled, autojump_clock, get_transcription):
    async with commands_context_flow_filled() as (context, context_delegate):
    
        await context.process_transcription(get_transcription('hello world'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Hello, world!'
        assert len(context._context_queue) == 2
        context_delegate.responses.clear()
        
        await context.process_transcription(get_transcription('bye'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Bye, world!'
        assert len(context._context_queue) == 1
        context_delegate.responses.clear()
        
        await context.process_transcription(get_transcription('hello'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 0
   
async def test_repeat_last_answer_response_action(commands_context_flow_filled, autojump_clock, get_transcription):
    async with commands_context_flow_filled() as (context, context_delegate):
    
        await context.process_transcription(get_transcription('hello world'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Hello, world!'
        context_delegate.responses.clear()
        assert len(context_delegate.responses) == 0
        
        await context.process_transcription(get_transcription('repeat'))
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == 'Hello, world!'
