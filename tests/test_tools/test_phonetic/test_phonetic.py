from pprint import pprint

import pytest

from stark.tools.phonetic.ipa import phonetic
from stark.tools.phonetic.simplephone import simplephone


@pytest.mark.parametrize(
    "lang,original_str,similar_str,common_simplified_str",
    [
        # English, German, Russian city names (should match phonetically)
        ("en", "Nürnberg", "Nuremberg", "NNPK"),
        ("en", "Nürnberg", "Нюрнберг", "NNPK"),
        # English hello/hallo, Cyrillic hello/hallo
        ("en", "hello", "hallo", "ALA"),
        ("ru", "хеллоу", "hallo", "ALA"),
        # Multi-language, exact match
        ("en", "hello", "hello", "ALA"),
        ("de", "hello", "hallo", "ALA"),
        # Music/brand names, cross-script
        ("en", "telegram", "телеграм", "TLKRM"),
        ("en", "led zeppelin", "ледзеплин", "LTSPPLN"),
        ("en", "imagine dragons", "имя джин драгонс", "AMJNTRKNS"),
        ("en", "highway to hell", "хайвей та хел", "HKTAL"),
        ("en", "linkin park", "линкольн парк", "LNKNPRK"),
        ("en", "spotify", "спу ти фай", "STPF"),
        # Multiword, Latin only
        ("en", "foo bar", "foobar", "FPA"),
        ("en", "bar baz", "barbaz", "BRPS"),
        ("en", "ber buz", "berbuz", "BRPS"),
    ]
)
def test_phonetic_equivalence(lang: str, original_str: str, similar_str: str, common_simplified_str):
    """
    Test that phonetic() produces the same simplified output for both strings,
    or at least that their simplephone encodings match if a common_simplified_str is provided.
    """
    pprint({
        "lang": lang,
        "original_str": original_str,
        "similar_str": similar_str,
        "common_simplified_str": common_simplified_str,
    })

    phonetic_orig = phonetic(original_str, lang)
    phonetic_sim = phonetic(similar_str, lang)
    simple_orig = simplephone(phonetic_orig)
    simple_sim = simplephone(phonetic_sim)

    print(f"phonetic({original_str!r}, {lang!r}) = {phonetic_orig!r} -> simplephone = {simple_orig!r}")
    print(f"phonetic({similar_str!r}, {lang!r}) = {phonetic_sim!r} -> simplephone = {simple_sim!r}")

    # Both should match the expected simplified string
    assert simple_orig == simple_sim == common_simplified_str
