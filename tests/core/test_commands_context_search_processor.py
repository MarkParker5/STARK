import asyncer
import pytest

from stark.core.commands_context_search_processor import CommandsContextSearchProcessor
from stark.core.commands_context_processor import CommandsContextLayer, ParsedType
from stark.core.patterns.pattern import Pattern
from stark.core.types.object import Object
from stark.core.commands_context import CommandsContext
from stark.core.commands_manager import CommandsManager
from stark.core.command import Response

# --- Test Types ---


from stark.general.classproperty import classproperty


class Location(Object[str]):
    def __init__(self, value):
        super().__init__(value)
        self.did_parse_called = False

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("*")

    async def did_parse(self, from_string: str) -> str:
        self.did_parse_called = True
        return from_string


class Person(Object[str]):
    def __init__(self, value):
        super().__init__(value)
        self.did_parse_called = False

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("*")

    async def did_parse(self, from_string: str) -> str:
        self.did_parse_called = True
        return from_string


class Date(Object[str]):
    def __init__(self, value):
        super().__init__(value)
        self.did_parse_called = False

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("*")

    async def did_parse(self, from_string: str) -> str:
        self.did_parse_called = True
        return from_string


class TCCSPFullName(Object):
    first_name: str
    second_name: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$first_name:Word $second_name:Word")


# Register types for pattern system
Pattern.add_parameter_type(Location)
Pattern.add_parameter_type(Person)
Pattern.add_parameter_type(Date)
Pattern.add_parameter_type(TCCSPFullName)


@pytest.fixture
def manager():
    return CommandsManager()


@pytest.fixture
async def context(manager):
    async with asyncer.create_task_group() as main_task_group:
        yield CommandsContext(main_task_group, manager)


@pytest.fixture
def processor():
    return CommandsContextSearchProcessor()


@pytest.fixture
def context_single_type(manager):
    @manager.new("go to $destination:Location")
    def go_to_destination(destination: Location) -> Response:
        return Response(text=f"Going to {destination.value}")

    cmd = manager.get_by_name("go_to_destination")
    return CommandsContextLayer(commands=[cmd], parameters={})


@pytest.fixture
def context_with_wrong_key(manager):
    @manager.new("go to $destination:Location")
    def go_to_destination(destination: Location) -> Response:
        return Response(text=f"Going to {destination.value}")

    cmd = manager.get_by_name("go_to_destination")
    return CommandsContextLayer(
        commands=[cmd], parameters={"wrong_key": Location("context_place")}
    )


@pytest.fixture
def context_precedence(manager):
    @manager.new("go to $destination:Location")
    def go_to_destination(destination: Location) -> Response:
        return Response(text=f"Going to {destination.value}")

    cmd = manager.get_by_name("go_to_destination")
    return CommandsContextLayer(
        commands=[cmd], parameters={"destination": Location("context_place")}
    )


@pytest.fixture
def context_nested(manager):
    @manager.new("register $name:TCCSPFullName")
    def register_name(name: TCCSPFullName) -> Response:
        return Response(text=f"Registered {name.first_name} {name.second_name}")

    cmd = manager.get_by_name("register_name")
    return CommandsContextLayer(commands=[cmd], parameters={})


@pytest.mark.asyncio
async def test_context_param_only(context, context_precedence):
    context._context_queue.insert(0, context_precedence)
    results = await context.process_string("go to nowhere")
    match = results[0].match_result
    obj = match.parameters.get("destination")
    assert obj is not None
    assert obj.value == "context_place"
    assert not obj.did_parse_called


@pytest.mark.asyncio
async def test_ner_only(context, context_single_type):
    context._context_queue.insert(0, context_single_type)
    ner_obj = Location("ner_place")
    context_parsed_types = [ParsedType(parsed_obj=ner_obj, parsed_substr="ner_place")]
    orig_processors = context.processors
    context.processors = [CommandsContextSearchProcessor()]
    results = await context.processors[0].process_context(
        "go to ner_place", context_single_type, context_parsed_types
    )
    match = results[0].match_result
    obj = match.parameters.get("destination")
    assert obj is not None
    assert obj.value == "ner_place"
    assert not obj.did_parse_called
    context.processors = orig_processors


@pytest.mark.asyncio
async def test_ner_precedence_over_context(context, context_precedence):
    context._context_queue.insert(0, context_precedence)
    ner_obj = Location("ner_place")
    context_parsed_types = [ParsedType(parsed_obj=ner_obj, parsed_substr="ner_place")]
    orig_processors = context.processors
    context.processors = [CommandsContextSearchProcessor()]
    results = await context.processors[0].process_context(
        "go to ner_place", context_precedence, context_parsed_types
    )
    match = results[0].match_result
    obj = match.parameters.get("destination")
    assert obj is not None
    assert obj.value == "ner_place"
    assert not obj.did_parse_called
    context.processors = orig_processors


@pytest.mark.asyncio
async def test_context_wrong_key(context, context_with_wrong_key):
    context._context_queue = [context_with_wrong_key]
    results = await context.process_string("go to nowhere")
    match = results[0].match_result
    assert match.parameters.get("destination") is None


@pytest.mark.asyncio
async def test_no_prefill(context, context_single_type):
    context._context_queue = [context_single_type]
    results = await context.process_string("go to Paris")
    match = results[0].match_result
    assert "destination" in match.parameters
    assert match.parameters.get("destination") is None


@pytest.mark.asyncio
async def test_last_state_nested_object(context, context_nested):
    context._context_queue.insert(0, context_nested)
    full_name_obj = TCCSPFullName("John Doe")
    full_name_obj.first_name = "John"
    full_name_obj.second_name = "Doe"
    parsed_types = [ParsedType(parsed_obj=full_name_obj, parsed_substr="John Doe")]
    orig_processors = context.processors
    context.processors = [CommandsContextSearchProcessor()]
    results = await context.processors[0].process_context(
        "register John Doe", context_nested, parsed_types
    )
    match = results[0].match_result
    assert isinstance(match.parameters.get("name"), TCCSPFullName)
    assert match.parameters["name"].first_name == "John"
    assert match.parameters["name"].second_name == "Doe"
    context.processors = orig_processors
