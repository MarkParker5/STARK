# Commands Context Documentation

## Introduction

The `Commands Context` feature provides a sophisticated means to manage multi-level command structures. By facilitating a hierarchical command interface, it ensures users enjoy an intuitive and seamless interaction.

## Managing Multiple Commands

In instances where a single input correlates with multiple commands, the system adeptly manages these overlaps. It gives priority to commands based on their position in the string or their declaration sequence, guaranteeing that the most pertinent command always takes precedence.

## The Contextual Hierarchy

Visualize the entire system as a tree. Each context functions as a node, with its linked sub-contexts acting as its offspring. As users navigate this tree, they move between nodes—either delving deeper or backtracking—to consistently find the right command match.

## Command Context Processing

When processing a string:

- The system adds the root context if it's missing.
- It checks the current context to find a command that matches the input string. If a command doesn't fit the current context, the system goes up, removing contexts until it finds a match or runs out of contexts.
- Upon a successful match, the system updates parameters, organizes dependencies, and initiates the command.
- Unneeded contexts are quickly removed.

## Managing Responses

Responses are neatly lined up. The system constantly checks this line, running responses and commands in the order they come in, ensuring fast and orderly processing.

## Response-embedded Context

Responses can include:

- **`needs_user_input: bool`**: If set to true, the system halts processing after the current response.
- **`commands: list[Command]`**: Commands that can reshape context, propose subsequent actions, or establish layered interfaces.
- **`parameters: dict[str, Any]`**: A supporting data list important for later processing or context definition.

For additional details on responses, visit the [Command Response](/command-response) page.

## Code Implementation

```python
@manager.new('hello', hidden=True) 
def hello_context(**params):
    voice = text = f'Hi, {params["name"]}!'
    return Response(text=text, voice=voice)

@manager.new('bye', hidden=True)
def bye_context(name: Word, handler: ResponseHandler):
    handler.pop_context()
    return Response(text=f'Bye, {name}!')

@manager.new('hello $name:Word')
def hello(name: Word):
    text = voice = f'Hello, {name}!'
    return Response(
        text=text,
        voice=voice,
        commands=[hello_context, bye_context],
        parameters={'name': name}
    )
```

The code example provided demonstrates how to define and manage commands using a fictional `manager` object.

1. **`hello_context` Function**:
   - This function is marked with a `hidden=True` parameter in its decorator. This means that the command will not be available in the root context, making it inaccessible as a top-level command.
   - The function accepts all context parameters through **params, which is a dictionary.
   - Within the function, both the `voice` and `text` variables are set to greet the user, using the context `name` parameter.
   - It then returns a response with the generated greeting text and voice.

2. **`bye_context` Function**:
   - Similarly, this function is also hidden from the root context.
   - The function accepts specific parameters: `name` and `handler`. It's important to note that there's no `name` in the command pattern, which implies that it must be derived from the context.
   - The `handler.pop_context()` method is called, which presumably removes the current context, signaling a transition or end of interaction.
   - A farewell response using the `name` parameter is returned.

3. **`hello` Function**:
   - This function defines a command pattern where a name is expected as input, formatted as hello $name.
   - Inside, it constructs a greeting using the provided name.
   - The response not only contains the greeting but also a list of commands (`hello_context` and `bye_context`) that can be triggered next. This showcases the hierarchical and contextual nature of the system. Additionally, the name is passed as a parameter for potential use in subsequent commands.

In summary, the code example gives us a glimpse into the contextual and hierarchical command management system. With the use of the `hidden` attribute, commands can be kept away from the root context, making them accessible only when they are contextually relevant.
