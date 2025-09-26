from pprint import pprint

import pytest

from stark.tools.phonetic.ipa import phonetic
from stark.tools.phonetic.simplephone import simplephone


@pytest.mark.parametrize(
    "original_str,similar_str",
    [
        ("en:foo bar", "en:foobar"),
        ("en:bar baz", "en:barbaz"),
        ("en:ber buz", "en:berbuz"),
        ("en:hello", "de:hallo"),
        ("en:hello", "ru:хеллоу"),
        ("en:hi", "ru:хай"),
        ("en:hey", "ru:хай"),
        ("de:Nürnberg", "en:Nuremberg"),
        ("de:Nürnberg", "ru:Нюрнберг"),
        ("en:telegram", "ru:телеграм"),
        ("en:led zeppelin", "ru:ледзеплин"),
        ("en:imagine dragons", "ru:имя джин драгонс"),
        ("en:linkin park", "ru:линкольн парк"),
        ("en:highway to hell", "ru:хайвей та хел"),
        ("en:spotify", "ru:спотифай"),
        ("en:spotify", "ru:спутифай"),
        ("en:spotify", "ru:с пути фай"),
        ("en:spotify", "ru:спу ти фай"),
    ]
)
def test_phonetic_equivalence(original_str: str, similar_str: str):
    """
    Test that phonetic() produces the same simplified output for both strings.
    """

    IGNORE_SPACES = True # vowels at the end of the word often add an extra A in the simplephone, while being ignored in the middle of the word

    # TODO: F vs W in ("en:highway to hell", "ru:хайвей та хел"),

    lang1, orig = original_str.split(':', 1)
    lang2, sim = similar_str.split(':', 1)
    pprint({
        "lang1": lang1,
        "orig": orig,
        "lang2": lang2,
        "sim": sim,
    })

    if IGNORE_SPACES:
        orig = orig.replace(' ', '')
        sim = sim.replace(' ', '')

    phonetic_orig = phonetic(orig, lang1)
    phonetic_sim = phonetic(sim, lang2)

    simple_orig = simplephone(phonetic_orig)
    simple_sim = simplephone(phonetic_sim)

    print(f"phonetic({orig!r}, {lang1!r}) = {phonetic_orig!r} -> simplephone = {simple_orig!r}")
    print(f"phonetic({sim!r}, {lang2!r}) = {phonetic_sim!r} -> simplephone = {simple_sim!r}")

    # Both should match
    assert simple_orig == simple_sim, f'{orig} -> {phonetic_orig} -> {simple_orig} != {simple_sim} <- {phonetic_sim} <- {sim}'
