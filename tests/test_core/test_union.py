import pytest

from stark.core.parsing import ParseError, PatternParser
from stark.core.patterns.pattern import Pattern
from stark.core.types import MakeUnion, Object, Union, any_subclass
from stark.general.classproperty import classproperty


# ── fixtures ──────────────────────────────────────────────────────────────────


class Num(Object):
    value: int

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(one|two|three)")

    async def did_parse(self, from_string) -> str:
        self.value = {"one": 1, "two": 2, "three": 3}[str(from_string).strip()]
        return from_string


class Word_(Object):
    """Minimal word type for union branch tests (avoids shadowing built-in Word)."""
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(apple|banana)")

    async def did_parse(self, from_string) -> str:
        self.value = str(from_string).strip()
        return from_string


class Digit(Object):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(1|2|3)")

    async def did_parse(self, from_string) -> str:
        self.value = str(from_string).strip()
        return from_string


# ── Union construction ─────────────────────────────────────────────────────────


def test_make_union_creates_union_subclass():
    U = MakeUnion(Num, Word_)
    assert issubclass(U, Union)
    assert U._types == [Num, Word_]


def test_pipe_operator_creates_union():
    U = Num | Word_
    assert issubclass(U, Union)
    assert set(U._types) == {Num, Word_}


def test_named_union_subclass():
    class Either(Union):
        _types = [Num, Word_]

    assert issubclass(Either, Union)
    assert Either._types == [Num, Word_]


# ── Union guards ───────────────────────────────────────────────────────────────


def test_direct_instantiation_blocked():
    with pytest.raises(TypeError, match="cannot be instantiated directly"):
        Union("x")


def test_pattern_override_blocked():
    with pytest.raises(TypeError, match="may not override 'pattern'"):
        class Bad(Union):
            _types = [Num]
            @classproperty
            def pattern(cls) -> Pattern: ...


def test_patterns_override_blocked():
    with pytest.raises(TypeError, match="may not override 'pattern'"):
        class Bad(Union):
            _types = [Num]
            @classproperty
            def patterns(cls): ...


# ── Union parsing + branch unwrap ─────────────────────────────────────────────


async def test_union_parses_first_branch():
    U = MakeUnion(Num, Word_)
    U.__name__ = "NumOrWord_"
    pp = PatternParser()
    pp.register_parameter_type(U)
    result = await pp.parse_object(U, "one extra")
    # parse_object on a Union returns the Union instance; .value is the matched branch
    assert isinstance(result.obj.value, Num)
    assert result.obj.value.value == 1


async def test_union_parses_second_branch():
    U = MakeUnion(Num, Word_)
    U.__name__ = "NumOrWord_2"
    pp = PatternParser()
    pp.register_parameter_type(U)
    result = await pp.parse_object(U, "apple extra")
    assert isinstance(result.obj.value, Word_)
    assert result.obj.value.value == "apple"


async def test_union_branch_unwrapped_as_parameter():
    """When a Union is used as a typed parameter, PatternParser unwraps it to the branch."""

    class Container(Object):
        item: object  # will be Num or Word_ directly, not the Union wrapper

        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("$item:NumOrWord_3")

        async def did_parse(self, from_string) -> str:
            return from_string

    U = MakeUnion(Num, Word_)
    U.__name__ = "NumOrWord_3"
    pp = PatternParser()
    pp.register_parameter_type(U)
    pp.register_parameter_type(Container)

    result = await pp.parse_object(Container, "two")
    assert isinstance(result.obj.item, Num)
    assert result.obj.item.value == 2

    result = await pp.parse_object(Container, "banana")
    assert isinstance(result.obj.item, Word_)
    assert result.obj.item.value == "banana"


async def test_named_union_parameter_not_unwrapped():
    """Named Union subclasses are opaque — the Union instance is passed through, branch via .value."""

    class NLPower(Union):
        _types = [Num, Word_]

    class Container(Object):
        power: NLPower

        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("$power:NLPower")

        async def did_parse(self, from_string) -> str:
            return from_string

    pp = PatternParser()
    pp.register_parameter_type(NLPower)
    pp.register_parameter_type(Container)

    result = await pp.parse_object(Container, "one extra")
    assert isinstance(result.obj.power, NLPower)
    assert isinstance(result.obj.power.value, Num)
    assert result.obj.power.value.value == 1


async def test_did_parse_override():
    log = []

    class Logged(Union):
        _types = [Num, Word_]

        async def did_parse(self, from_string) -> str:
            result = await super().did_parse(from_string)
            log.append(type(self.value).__name__)
            return result

    pp = PatternParser()
    pp.register_parameter_type(Logged)
    await pp.parse_object(Logged, "one extra")
    assert log == ["Num"]


# ── auto-registration ──────────────────────────────────────────────────────────


async def test_auto_registration_registers_dep_tree():
    class Root(Union):
        _types = [Num, Word_]

    pp = PatternParser()
    pp.register_parameter_type(Root)
    assert "Num" in pp.parameter_types_by_name
    assert "Word_" in pp.parameter_types_by_name
    assert Root.__name__ in pp.parameter_types_by_name


async def test_auto_registration_idempotent():
    class Root2(Union):
        _types = [Num, Digit]

    pp = PatternParser()
    pp.register_parameter_type(Root2)
    pp.register_parameter_type(Root2)  # second call must be a no-op
    pp.register_parameter_type(Num)    # already in tree, must be a no-op
    assert list(pp.parameter_types_by_name).count("Num") == 1


async def test_auto_registration_handles_shared_dep():
    """Two union types sharing a branch — branch registered only once."""

    class U1(Union):
        _types = [Num, Word_]

    class U2(Union):
        _types = [Num, Digit]

    pp = PatternParser()
    pp.register_parameter_type(U1)
    pp.register_parameter_type(U2)
    assert list(pp.parameter_types_by_name).count("Num") == 1


# ── any_subclass ───────────────────────────────────────────────────────────────


def test_any_subclass_discovers_all():
    class Base(Object):
        @classproperty
        def pattern(cls) -> Pattern:
            raise NotImplementedError

    class Sub1(Base):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("sub1")

    class Sub2(Base):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("sub2")

    U = any_subclass(Base)
    assert issubclass(U, Union)
    assert set(U._types) == {Sub1, Sub2}


def test_any_subclass_name_has_no_pipe():
    class BaseUnit(Object):
        @classproperty
        def pattern(cls) -> Pattern:
            raise NotImplementedError

    class UnitA(BaseUnit):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("a")

    class UnitB(BaseUnit):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("b")

    U = any_subclass(BaseUnit)
    assert "|" not in U.__name__


def test_any_subclass_cached():
    class BaseCached(Object):
        @classproperty
        def pattern(cls) -> Pattern:
            raise NotImplementedError

    class CachedSub(BaseCached):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("x")

    U1 = any_subclass(BaseCached)
    U2 = any_subclass(BaseCached)
    assert U1 is U2


async def test_any_subclass_fstring_sugar():
    """any_subclass(T) can be used directly in an f-string pattern — no .__name__ needed."""

    class BaseF(Object):
        @classproperty
        def pattern(cls) -> Pattern:
            raise NotImplementedError

    class SubF1(BaseF):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("alpha")

        async def did_parse(self, from_string) -> str:
            self.value = "alpha"
            return from_string

    class SubF2(BaseF):
        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("beta")

        async def did_parse(self, from_string) -> str:
            self.value = "beta"
            return from_string

    class Container(Object):
        item: BaseF

        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern(f"$item:{any_subclass(BaseF)}")  # no .__name__

        async def did_parse(self, from_string) -> str:
            return from_string

    pp = PatternParser()
    pp.register_parameter_type(Container)

    result = await pp.parse_object(Container, "alpha")
    assert isinstance(result.obj.item, SubF1)

    result = await pp.parse_object(Container, "beta")
    assert isinstance(result.obj.item, SubF2)


async def test_abstract_base_registration_blocked():
    class AbstractUnit(Object):
        @classproperty
        def pattern(cls) -> Pattern:
            raise NotImplementedError

    pp = PatternParser()
    with pytest.raises(NotImplementedError):
        pp.register_parameter_type(AbstractUnit)
