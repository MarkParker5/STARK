import time
from pympler.asizeof import asizeof
import pytest

from stark.tools.dictionary.dictionary import Dictionary, LookupMode, NameEntry
from stark.tools.dictionary.storage.storage_memory import (
    DictionaryStorageMemory,
)
from stark.tools.dictionary.storage.storage_sqlite import (
    DictionaryStorageSQLite,
)
import random
from faker import Faker


# Benchmark
# @pytest.mark.timeout(30.0)
@pytest.mark.benchmark(
    timer=time.monotonic,
    min_time=0.1,
    max_time=1.0,
)
# Report
@pytest.mark.report_duration
@pytest.mark.report_tracemalloc
# Parametrize
# @pytest.mark.parametrize("dict_size", [100, 1_000, 10_000])
@pytest.mark.parametrize("dict_size", [100, 1_000, 10_000, 100_000])
@pytest.mark.parametrize("success", [True, False])
@pytest.mark.parametrize(
    "lookup_mode",
    # [LookupMode.FUZZY, LookupMode.UNTIL_MATCH],
    [LookupMode.EXACT, LookupMode.CONTAINS, LookupMode.FUZZY, LookupMode.UNTIL_MATCH],
)
@pytest.mark.parametrize("lookup_func", ["lookup"])  # , "sentence_search"])
@pytest.mark.parametrize("storage_type", ["memory"])  # , "sqlite"])
# Other
def test_benchmark__dictionary(
    # benchmark cases
    dict_size: int,
    success: bool,
    lookup_mode: LookupMode,
    lookup_func: str,
    storage_type: str,
    # fixtures
    benchmark,
    # additional parameters
    seed: int | None = None,
):
    # params that are not part of the parametrized cases and just randomly generated
    ner_type = random.choice(["name", "place"])
    targets_amount = random.choice([1, 1, 1, 2, 3])
    sentence_length = random.randint(5, 15)
    print(f"{success=}, {ner_type=}, {targets_amount=}, {sentence_length=}")

    fake = Faker("en")

    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # Generate unique names

    names_set: set[str] = set()
    while len(names_set) < dict_size:
        if ner_type == "name":
            names_set.add(fake.unique.name())
        elif ner_type == "place":
            names_set.add(
                random.choice(
                    [
                        fake.street_name(),
                        fake.city(),
                        fake.state(),
                        fake.country(),
                        fake.location_on_land()[2],
                    ]
                )
            )
    names: list[str] = list(names_set)

    # Select name(s) to search

    targets: set[str] = set()
    for i in range(targets_amount):
        if success:
            targets.add(names[i])
        else:
            targets.add(names.pop())
    first_target = list(targets)[0]

    # Prepare sentence

    sentence = fake.sentence(nb_words=sentence_length)
    words = sentence.split()
    for target in targets:
        index = random.randint(0, len(words) - 1)
        words[index] += " " + target
    sentence = " ".join(words)

    # Fill the dictionary

    if storage_type == "memory":
        dictionary = Dictionary(DictionaryStorageMemory())
    elif storage_type == "sqlite":
        dictionary = Dictionary(DictionaryStorageSQLite(":memory:"))
    else:
        raise ValueError(f"Invalid storage type: {storage_type}")

    entries = [
        NameEntry(language_code="en", name=n, metadata={"idx": i})
        for i, n in enumerate(names)
    ]
    dictionary.write_all(entries)

    # Log RAM usage after build

    dictionary_ram = asizeof(dictionary) // 1024**2  # MB
    print(f"RAM usage after loading {dict_size} entries: {dictionary_ram:.2f} MB")
    assert dictionary_ram < 900, "RAM usage exceeded 900MB"

    # Run benchmarks

    def execute_lookup():
        if lookup_func == "lookup":
            return list(dictionary.lookup(first_target, "en", mode=lookup_mode))
        elif lookup_func == "sentence_search":
            return list(dictionary.sentence_search(sentence, "en", mode=lookup_mode))
        else:
            raise ValueError(f"Invalid lookup function: {lookup_func}")

    if benchmark:
        result = benchmark(execute_lookup)
    else:
        result = execute_lookup()

    if success:
        assert result


# not asserting false success due to possible similar entries


# @pytest.mark.benchmark
# @pytest.mark.parametrize(
#     "to_ipa", [to_ipa__espeak_cli, to_ipa__espeak_bin, to_ipa__epitran]
# )
# def test_benchmark__to_ipa(benchmark, to_ipa: Callable[[str, str], str]):
#     from faker import Faker

#     locales = {
#         "en": "en_US",
#         "es": "es_ES",
#         "fr": "fr_FR",
#         "de": "de_DE",
#         "it": "it_IT",
#         "uk": "uk_UA",
#         "ru": "ru_RU",
#         "nl": "nl_NL",
#     }

#     faker_objects = {lang: Faker(loc) for lang, loc in locales.items()}

#     test_cases = [
#         f"{lang}:{faker_objects[lang].sentence(nb_words=faker_objects[lang].random_int(min=3, max=30))}"
#         for lang in locales
#         for _ in range(10)
#     ]

#     # print(test_cases)

#     def test():
#         for case in test_cases:
#             language, text = case.split(":")
#             assert to_ipa(text, language)

#     test()  # warm up to instantiate lazy cached deps
#     benchmark(test)  # run the benchmark
