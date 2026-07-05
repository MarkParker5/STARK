# Fallback Command / LLM Integration

In the dynamic world of voice assistants and speech recognition, it's essential to account for the unpredictability of user input. Despite the comprehensive list of commands you may have configured, there will inevitably be instances where user utterances don't align with any predefined command. This is where the fallback command comes in.

The fallback command in the STARK framework serves as a safety net, ensuring that when a user's voice input doesn't match any set command, there's still an appropriate and meaningful response.

## Setting Up the Fallback Command

A fallback command is just a regular command with a wildcard pattern, `$string:String` matches anything. Two things matter for it to actually behave like a fallback:

```python
from stark.core.types import String
...

@manager.new('$string:String')  # NOT hidden=True — see below
async def fallback(string: String):
    # Your fallback logic here
    ...

manager.extend(fallback_manager)  # register it LAST
```

1. **Don't mark it `hidden=True`.** A `hidden=True` command is never added to the manager's command list at all, it only becomes reachable when explicitly offered via a `Response`'s `commands=[...]` (see [Commands Context](https://stark.markparker.me/commands-context/index.md)). A fallback needs to be reachable from anywhere, all the time, so it can't be hidden.
1. **Register it last.** [`SearchProcessor`](https://stark.markparker.me/advanced/custom-processors/index.md) resolves overlapping matches in favor of the command added earliest. Since `$string:String` overlaps with almost everything, it has to be the last command added, merge its manager in after every other command is registered, so specific commands always win.

This is simple, but it's a soft guarantee, a wildcard pattern technically *can* still win in edge cases depending on match overlap. For a hard guarantee that the fallback only fires when truly nothing else matched, see the alternative below.

### A More Reliable Alternative

Keep the command `hidden=True` (so it's never in the regular match pool at all) and add a final pipeline stage that runs only after every other processor has had a chance and found nothing:

```python
from stark.core.commands_context_processor import CommandsContextProcessor
from stark.core.commands_manager import SearchResult
from stark.core.parsing import MatchResult

@manager.new('$string:String', hidden=True)
async def fallback(string: String):
    # Your fallback logic here
    ...

class FallbackProcessor(CommandsContextProcessor):
    async def process_context_layer(self, string, context, context_layer, recognized_entities):
        match = MatchResult(substring=str(string), start=0, end=len(string), parameters={'string': string})
        return [SearchResult(command=fallback, match_result=match)]  # always matches

context = CommandsContext(
    ...,
    processors=[SearchProcessor(), FallbackProcessor()],  # only reached if SearchProcessor found nothing
)
```

See [Custom Processors](https://stark.markparker.me/advanced/custom-processors/index.md) for the full pipeline mechanics, a processor only runs if every processor before it returned no results.

## Fallback Command Options

With the rise of advanced language models like ChatGPT, it's now feasible to provide intelligent and contextually relevant responses even for unexpected user inputs. Integrating an LLM can elevate the user experience, making your voice assistant appear more intuitive and responsive.

Fallbacks aren't limited to LLMs. You can get creative with your approach. Consider these options:

- **Wikipedia API**: Search for a quick answer or definition related to the user's query.
- **Google Search Parsing**: Extract snippets from top search results for a quick response.
- **Custom Database Lookups**: If you have a specific dataset or database, direct fallback queries there.
- **Fun random "I don't know" synonyms**

______________________________________________________________________

Fallback commands are invaluable, ensuring your voice assistant remains responsive, intelligent, and user-friendly, even in the face of unexpected inputs. With the flexibility of STARK and the power of modern Large Language Models, creating a robust voice assistant has never been easier.

Want the LLM itself to take action instead of just answering, running a search, controlling a device, taking multiple steps? See [AI Agent Platform](https://stark.markparker.me/agent-platform/index.md) for where this is headed in v5.
