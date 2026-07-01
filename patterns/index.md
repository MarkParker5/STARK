# Patterns

Patterns in the S.T.A.R.K toolkit are designed to be dynamic and extensible. They are at the core of how custom voice assistants interpret input and match it to commands. This documentation is a comprehensive guide to understanding and working with patterns in S.T.A.R.K.

## Pattern Syntax

At its essence, a pattern is a string that defines the structure of input it should match. The pattern syntax is enriched with special characters and sequences to help it match a variety of inputs dynamically.

### Basics

- `**`: Matches any sequence of words.
- `*`: Matches any single word.
- `$name:Type`: Defines a named parameter of a specific type.

Example: For instance, the pattern `'Some ** here'` will match both `'Some text here'` and `'Some lorem ipsum dolor here'`.

### Advanced Syntax

**Selections** Selections provide flexibility in your voice command patterns by allowing multiple possibilities for a single command spot. This can be particularly useful in accommodating various ways users might phrase the same request.

- `(foo|bar|baz)`: This pattern matches any single option among the three. So, it will match either `'foo'`, `'bar'`, or `'baz'`. Think of it as an "OR" choice for the user.
- `(foo|bar)?`: This pattern introduces an optional choice. It can match `'foo'`, `'bar'`, or neither. The `?` denotes that the preceding pattern (in this case, the choice between `'foo'` or `'bar'`) is optional.
- `{foo|bar}`: This pattern is designed to capture repetitions. It matches one or more occurrences of `'foo'` or `'bar'`. For example, if a user said "foo foo bar", this pattern would successfully match. Note: Be cautious with this pattern as it can match long, unexpected repetitions.

There are also two plain-text helper functions for ordered groups:

```python
from stark.core.patterns.rules import one_from, one_or_more_from
```

- `one_from(*args)` → `(a|b|c)`
- `one_or_more_from(*args)` → `{a|b|c}`

General Tip: While creating patterns, always keep the user's natural way of speaking in mind. Testing your patterns with real users can help ensure that your voice assistant responds effectively to a variety of commands.

## Parameters Parsing

Voice commands can be dynamic, meaning they can accommodate varying inputs. This is achieved using named parameters in the command pattern, with the `$name:Type` syntax. When a user input matches a pattern with named parameters, the assistant extracts these parameters and passes them to the corresponding function.

For example, consider the pattern `'Hello $name:Word'`. If a user says, `'Hello Stark'`, the system will extract a parameter named `'name'` with the value `'Stark'`.

However, ensure that the function declaration tied to a command pattern includes all the parameters defined in that pattern, using the same names and types. If this isn't done, you'll encounter an exception during command creation.

Here's an example:

```python
from stark.core.types import Word

@manager.new('Hello $name:Word')
async def example_function(name: Word) -> Response:
    return Response(f'You said {name}!')
```

## Native Types List

Out of the box, the S.T.A.R.K. comes with native types that can be used as parameter types in patterns. The currently supported native types include:

- `String`: Matches any sequence of words (\*\*).
- `Word`: Matches a single word (\*).

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

context = CommandsContext(...)
context.pattern_parser.register_parameter_type(FullName)
```

Upon successfully matching the pattern, S.T.A.R.K will autonomously parse and assign values to `first_name` and `second_name`. It's imperative, just as with command patterns, that class properties are congruent with the pattern in terms of both name and type.

The section is well-detailed, but I have a few recommendations to make it even clearer:

______________________________________________________________________

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
        The from_string argument is a LocaleString — same as the regular string, but provides `from_string.language_code: LanguageCode`
        for language-aware parsing. See Localization docs for details.
        '''

        if 'lorem' not in from_string:
            raise ParseError('lorem not found') # Throw a ParseError if the string doesn't meet certain criteria

        self.value = 'lorem' # Assign additional properties (properties inferred from the pattern are auto-assigned)
        return 'lorem' # Return the smallest substring essential for this object

context = CommandsContext(...)
context.pattern_parser.register_parameter_type(Lorem)
print(context.pattern_parser.parse_object(Lorem, "lorem ipsum"))
```

## Custom Parser Class Example

In some cases, you may want to separate the parsing logic from your data model. This is especially useful when you want to reuse parsing logic, inject dependencies, have longer life cycle (stateful parser), or just keep your models clean. You can define a dedicated parser class for your object type.

Here's an example:

```python
from stark.core.types import Object, Word
from stark.core.parsing import Pattern, PatternParser, ObjectParser

class Lorem(Object):
    @classproperty
    def pattern(cls):
        return Pattern("* ipsum")

class LoremParser(ObjectParser):
    def __init__(self, pattern_parser: PatternParser):
        self.pattern_parser = pattern_parser

    async def did_parse(self, obj: Lorem, from_string: str) -> str:
        # Custom parsing logic for Lorem
        if "lorem" not in from_string:
            raise ParseError("lorem not found")
        obj.value = "lorem"
        return "lorem"

context = CommandsContext(...)
context.pattern_parser.register_parameter_type(Lorem, parser=LoremParser())
print(context.pattern_parser.parse_object(Lorem, "lorem ipsum"))
```

This approach allows you to keep parsing logic separate from your data model and makes it easy to inject dependencies or share logic between different models.

Note that the `did_parse` method must return a substring of the input string that was successfully parsed. This substring should be the smallest possible string that still represents the object's value. In case you use 3rd party parser that can't extract substring and just provides the value, you have several options to handle this:

1. If your parser returns a string-ish value, like some kind of name, you can use `levenshtein_search_substring` from the [STARK-Levenshtein](https://stark.markparker.me/tools/stark-levenshtein/index.md) module. This will allow you efficiently find the closest fuzzy match of your named entity in the input string.
1. Consider using `NLDictionaryName` from [Phonetic Dictionary](https://stark.markparker.me/tools/phonetic-dictionary/index.md) if suits your needs.
1. If options above are not suitable, take a look at [sliding_window_parser](https://stark.markparker.me/tools/sliding-window-parser/index.md) wrapper. Note that it will call the parser method multiple times to find the best match, which can be optimized by caching intermediate results inside your parser func, but yet still requires careful usage especially with large input strings and long io-bound parsing times.

## Recommended Use of Caching for `did_parse` Method

When the `did_parse` method is involved in the matching process, especially if it performs complex computations or external lookups, it can slow down the overall matching process. To alleviate this potential bottleneck, it's highly recommended to use caching. By storing previously parsed objects in a cache, you can avoid redundant work and improve the overall performance of your custom voice assistant.

______________________________________________________________________

## (beta) Unordered Patterns

By default, parameters in a pattern must appear in a fixed order. Unordered patterns relax this constraint. The user can say the parts in any order and S.T.A.R.K will still match them.

There are two flavours, available as helper functions from `stark.core.patterns.rules`:

### `all_unordered(*args)`, all required

Every listed element must be present in the input. Order doesn't matter.

```python
from stark.core.patterns.rules import all_unordered

pattern = Pattern(f"{all_unordered('$h:Hours', '$m:Minutes', '$s:Seconds')}")
# matches "12 h 30 m 45 s", "45 s 12 h 30 m", etc.
# does NOT match "12 h 30 m" (missing seconds)
```

### `one_or_more_unordered(*args)`, at least one required

At least one element must match. The rest are optional. Order doesn't matter.

```python
from stark.core.patterns.rules import one_or_more_unordered

pattern = Pattern(f"{one_or_more_unordered('$h:Hours', '$m:Minutes', '$s:Seconds')}")
# matches "12 h 30 m 45 s", "12 h", "30 m 45 s", etc.
# does NOT match "" (at least one must be present)
```

> **Note:** Unordered patterns use lookahead-based matching under the hood and don't work well with multi-word wildcards (`**`). For unordered multi-word parameters, use Slots instead.

## Union Types

A `Union` parameter type matches one of several concrete types and routes parsing to whichever branch succeeds. There are three declaration styles:

### Factory (`MakeUnion` / `|`)

```python
from stark.core.types import MakeUnion

NLPower = NLMeasurementWatt | NLMeasurementVolt
NLPower = MakeUnion(NLMeasurementWatt, NLMeasurementVolt) # equivalent
```

Use the factory or pipe when the union is a one-off composition. Factory unions are **transparent**: when used as a typed parameter, the parser unwraps to the matched branch directly, so `self.power` is an `NLMeasurementWatt` or `NLMeasurementVolt` instance.

### Named subclass

```python
from stark.core.types import Union

class NLPower(Union):
    _types = [NLMeasurementWatt, NLMeasurementVolt]
```

Named unions are **opaque**: if used as a typed parameter, `self.power` will be an `NLPower` instance with `.value` holding the matched branch. Use when you want to extend `did_parse` behavior for the union as a whole, but don't forget to call `super().did_parse`.

### `any_subclass` factory

By default, STARK only tries to parse the exact type of the parameter and ignores any parent/child classes. `any_subclass(T)` where `T` is a subclass of `Object` recursively discovers all subclasses of `T` and returns a transparent Union of them (i.e. the union is unwrapped to the matched subclass automatically).

```python
from stark.core.types import any_subclass

class NLUnit(Object):
    pint_unit: str

    @classproperty
    def pattern(cls) -> Pattern:
        raise NotImplementedError  # prevents direct registration

class NLUnitWatt(NLUnit):
    pint_unit = "watt"
    @classproperty
    def pattern(cls) -> Pattern: return Pattern("(watt|w)")

class NLUnitVolt(NLUnit):
    pint_unit = "volt"
    @classproperty
    def pattern(cls) -> Pattern: return Pattern("(volt|v)")

class NLMeasurement(Object):
    number: NLNumber
    unit: NLUnit

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern(f"$number:NLNumber $unit:{any_subclass(NLUnit)}")

    async def did_parse(self, from_string) -> str:
        assert self.number and self.unit and self.unit.pint_unit  # all parsed automatically
        self.value = (self.unit.pint_unit, self.number.value)
        return from_string
```

In this example, because of `any_subclass(NLUnit)` in the pattern, `PatternParser` would try to parse `unit` property of `NLMeasurement` using subclasses of `NLUnit` instead of trying to parse parental class `NLUnit` iteself.

`register_parameter_type(NLMeasurement)` registers the entire tree automatically — no explicit list, no manual registration of each unit type.

To add a new unit, simply define a subclass of `NLUnit` before the first `register_parameter_type` call (all subclasses are discovered automatically):

```python
class NLUnitAmpere(NLUnit):
    pint_unit = "ampere"
    @classproperty
    def pattern(cls) -> Pattern: return Pattern("(ampere|amp|a)")
```

## Slots

Slots provide unordered parameter extraction for Object types with multiple fields. Unlike unordered patterns (which work at the pattern level), Slots parse each field independently from the input string, so they handle multi-word and greedy parameters correctly.

### Defining a Slots class

A Slots class is a regular `Object` subclass. Each annotated field (except `value`) becomes a slot that will be parsed independently. Fields can be required or optional (`Optional[T]` / `T | None`).

```python
from typing import Optional
from stark.core.types import Object, Word

class TimerSlots(Object):
    hours: Hours           # required
    minutes: Minutes       # required
    seconds: Optional[Seconds]  # optional

    # NOTE: no pattern needed for TimerSlots
```

### Registering with SlotsParser

Unlike regular Object types, Slots classes use `SlotsParser` instead of the default parser:

```python
from stark.core.types.slots import SlotsParser

context = CommandsContext(...)
context.pattern_parser.register_parameter_type(
    TimerSlots,
    parser=SlotsParser(context.pattern_parser) # <-
)
```

### Using Slots in patterns

Reference the Slots class like any other parameter type:

```python
@manager.new('set timer $timer:TimerSlots')
async def set_timer(timer: TimerSlots) -> Response:
    h = timer.hours       # Hours object or None
    m = timer.minutes     # Minutes object
    s = timer.seconds     # Seconds object or None
    ...
```

### How it works

`SlotsParser` iterates over each slot and tries to parse its type from the remaining input string. Successfully parsed substrings are removed before parsing the next slot. After all slots are processed:

- At least one slot must have matched, otherwise parsing fails.
- Required (non-optional) slots must all match, otherwise parsing fails.
- The `value` property is set to the minimal substring spanning all matched slots.

This makes Slots ideal for commands where parameters can appear in any order and may include multi-word values, something that pattern-based unordered matching can't handle reliably.

______________________________________________________________________

By understanding and mastering patterns in the S.T.A.R.K toolkit, you'll be well-equipped to create powerful and dynamic custom voice assistants. Happy coding!

Pattern matching itself runs as one stage in a pluggable pipeline, see [Custom Processors](https://stark.markparker.me/advanced/custom-processors/index.md) if you want to add your own stage (e.g. NER, phonetic correction) before or after matching.
