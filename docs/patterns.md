# Patterns

Patterns in the S.T.A.R.K toolkit are designed to be dynamic and extensible. They are at the core of how custom voice assistants interpret input and match it to commands. This documentation is a comprehensive guide to understanding and working with patterns in S.T.A.R.K.

## Pattern Syntax

At its essence, a pattern is a string that defines the structure of input it should match. The pattern syntax is enriched with special characters and sequences to help it match a variety of inputs dynamically.

### Basics

- `**`: Matches any sequence of words.
- `*`: Matches any single word.
- `$name:Type`: Defines a named parameter of a specific type.

Example:
For instance, the pattern `'Some ** here'` will match both `'Some text here'` and `'Some lorem ipsum dolor here'`.

### Advanced Syntax

**Selections**
Selections provide flexibility in your voice command patterns by allowing multiple possibilities for a single command spot. This can be particularly useful in accommodating various ways users might phrase the same request.

- `(foo|bar|baz)`: This pattern matches any single option among the three. So, it will match either `'foo'`, `'bar'`, or `'baz'`. Think of it as an "OR" choice for the user.

- `(foo|bar)?`: This pattern introduces an optional choice. It can match `'foo'`, `'bar'`, or neither. The `?` denotes that the preceding pattern (in this case, the choice between `'foo'` or `'bar'`) is optional.

- `{foo|bar}`: This pattern is designed to capture repetitions. It matches one or more occurrences of `'foo'` or `'bar'`. For example, if a user said "foo foo bar", this pattern would successfully match. Note: Be cautious with this pattern as it can match long, unexpected repetitions.

General Tip: While creating patterns, always keep the user's natural way of speaking in mind. Testing your patterns with real users can help ensure that your voice assistant responds effectively to a variety of commands.

## Parameters Parsing

Voice commands can be dynamic, meaning they can accommodate varying inputs. This is achieved using named parameters in the command pattern, with the `$name:Type` syntax. When a user input matches a pattern with named parameters, the assistant extracts these parameters and passes them to the corresponding function.

For example, consider the pattern `'Hello $name:Word'`. If a user says, `'Hello Stark'`, the system will extract a parameter named `'name'` with the value `'Stark'`.

However, ensure that the function declaration tied to a command pattern includes all the parameters defined in that pattern, using the same names and types. If this isn't done, you'll encounter an exception during command creation.

Here's an example:

```python
from stark.types import Word

@manager.new('Hello $name:Word')
async def example_function(name: Word) -> Response:
    text = voice = f'You said {name}!'
    return Response(text=text, voice=voice)
```

## Native Types List

Out of the box, the S.T.A.R.K. comes with native types that can be used as parameter types in patterns. The currently supported native types include:

- `String`: Matches any sequence of words (**).
- `Word`: Matches a single word (*).

It's also worth noting that you can extend the list of types by defining custom object types, as we'll discuss in the next section.

## Defining Custom Object Types

The S.T.A.R.K toolkit isn't just limited to native types; it empowers developers to define their own custom object types. These bespoke types are constructed by subclassing the `Object` base class and specifying a distinct matching pattern. 

A standout feature of the S.T.A.R.K toolkit's patterns is their seamless compatibility with nested objects. In essence, a custom object type can house parameters that are, in themselves, other custom object types. This nesting capability facilitates the crafting of complex and nuanced patterns, capable of interpreting diverse input configurations.

Below is a demonstrative example of how one might structure a custom object type:

```python
class FullName(Object):
    first_name: Word
    second_name: Word
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$first_name:Word $second_name:Word')
```

Upon successfully matching the pattern, S.T.A.R.K will autonomously parse and assign values to `first_name` and `second_name`. It's imperative, just as with command patterns, that class properties are congruent with the pattern in terms of both name and type.

The section is well-detailed, but I have a few recommendations to make it even clearer:

---

## Advanced Object Types with Parsing Customization

In instances where the default parsing doesn't cater to your requirements, or when you need specialized processing, the `did_parse` method comes to the rescue. By overriding this method in custom object types, you can introduce intricate transformations or run custom validation checks post-parsing.

Here's an illustrative example:

```python
class Lorem(Object):
    
    @classproperty
    def pattern(cls):
        return Pattern('* ipsum')
    
    async def did_parse(self, from_string: str) -> str:
        '''
        Invoked after parsing from the string and assigning the parameters detected in the pattern.
        Directly calling this method is typically unnecessary and uncommon.
        
        Override this method to achieve more sophisticated string parsing. 
        '''
        
        if 'lorem' not in from_string:
            raise ParseError('lorem not found') # Throw a ParseError if the string doesn't meet certain criteria

        self.value = 'lorem' # Assign additional properties (properties inferred from the pattern are auto-assigned)
        return 'lorem' # Return the smallest substring essential for this object
```

## Recommended Use of Caching for `did_parse` Method

When the `did_parse` method is involved in the matching process, especially if it performs complex computations or external lookups, it can slow down the overall matching process. To alleviate this potential bottleneck, it's highly recommended to use caching. By storing previously parsed objects in a cache, you can avoid redundant work and improve the overall performance of your custom voice assistant.

---

By understanding and mastering patterns in the S.T.A.R.K toolkit, you'll be well-equipped to create powerful and dynamic custom voice assistants. Happy coding!
