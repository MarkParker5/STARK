import anyio
from typing_extensions import Optional

from stark.core import Pattern, Response
from stark.core.types import Object
from stark.general.classproperty import classproperty


async def test_command_flow_optional_parameter(commands_context_flow, autojump_clock):
    async with commands_context_flow() as (manager, context, context_delegate):

        class Category(Object):
            @classproperty
            def pattern(cls) -> Pattern:
                return Pattern("c*")

        class Device(Object):
            @classproperty
            def pattern(cls) -> Pattern:
                return Pattern("d*")

        class Room(Object):
            @classproperty
            def pattern(cls) -> Pattern:
                return Pattern("r*")

        context.pattern_parser.register_parameter_type(Category)
        context.pattern_parser.register_parameter_type(Device)
        context.pattern_parser.register_parameter_type(Room)

        @manager.new("turn on ($category:Category|$device:Device|$room:Room)")
        def turn_on(category: Optional[Category], device: Optional[Device], room: Optional[Room]) -> Response:
            if category:
                return Response(text=f"Category {category.value}")
            elif device:
                return Response(text=f"Device {device.value}")
            elif room:
                return Response(text=f"Room {room.value}")
            else:
                raise ValueError("No category, device or room provided")

        print(context.pattern_parser._compile_pattern(turn_on.pattern))

        await context.process_string("turn on cooling")
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 1
        assert context_delegate.responses[0].text == "Category cooling"

        await context.process_string("turn on dishwasher")
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 2
        assert context_delegate.responses[1].text == "Device dishwasher"

        await context.process_string("turn on restroom")
        await anyio.sleep(5)
        assert len(context_delegate.responses) == 3
        assert context_delegate.responses[2].text == "Room restroom"
