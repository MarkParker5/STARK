# Fallback Command / LLM Integration

In the dynamic world of voice assistants and speech recognition, it's essential to account for the unpredictability of user input. Despite the comprehensive list of commands you may have configured, there will inevitably be instances where user utterances don't align with any predefined command. This is where the fallback command comes in.

The fallback command in the STARK framework serves as a safety net, ensuring that when a user's voice input doesn't match any set command, there's still an appropriate and meaningful response.

## Setting Up the Fallback Command

In the STARK framework, integrating a fallback command is streamlined. You can assign the `fallback_command` to the `CommandsContext` directly:

```python
CommandsContext.fallback_command: Command
```

Here's a practical example:

```python
from stark.core.types import String
...

@manager.new('$string:String', hidden=True)
async def fallback(string: String):
    # Your fallback logic here
    ...

commands_context.fallback_command = fallback
```

In this example, any unrecognized string is directed to the `fallback` function, allowing you to define how the system should respond.

## Fallback Command Options

With the rise of advanced language models like ChatGPT, it's now feasible to provide intelligent and contextually relevant responses even for unexpected user inputs. Integrating an LLM can elevate the user experience, making your voice assistant appear more intuitive and responsive.

Fallbacks aren't limited to LLMs. You can get creative with your approach. Consider these options:

- **Wikipedia API**: Search for a quick answer or definition related to the user's query.
- **Google Search Parsing**: Extract snippets from top search results for a quick response.
- **Custom Database Lookups**: If you have a specific dataset or database, direct fallback queries there.
- **Fun random "I don't know" synonyms**

---

Fallback commands are invaluable, ensuring your voice assistant remains responsive, intelligent, and user-friendly, even in the face of unexpected inputs. With the flexibility of STARK and the power of modern Large Language Models, creating a robust voice assistant has never been easier.
