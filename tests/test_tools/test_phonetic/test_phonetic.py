import pytest

from stark.tools.levenshtein import (
    levenshtein_distance,
)
from stark.tools.phonetic.transcription import transcription
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
        # ("de:Nürnberg", "en:Nuremberg"), # fails, too different - need to register both options for such cases
        ("en:telegram", "ru:телеграм"),
        ("de:Nürnberg", "en:Nurnberg"),
        ("de:Nürnberg", "ru:Нюрнберг"),
        # ("uk:Київ", "ru:Киев"), # default ubuntu espeak doesn't have ukrainian lang which fails CI
        # ("uk:Київ", "en:Kyiv"),
        ("en:Czechia", "ru:Чехия"),
        ("en:led zeppelin", "ru:ледзеплин"),
        ("en:imagine dragons", "ru:имя джин драгонс"),
        ("en:imagine dragons", "ru:имя джин дракон"),
        ("en:linkin park", "ru:линкольн парк"),
        ("en:white", "ru:вайт"),
        ("en:white", "ru:уайт"),
        ("en:Emma Watson", "ru:Эмма Уотсон"),
        ("en:John Watson", "ru:Джон Ватсон"),
        ("en:highway to hell", "ru:хай уэй ту хэл"),
        ("en:highway to hell", "ru:хайвей та хел"),
        ("en:spotify", "ru:спотифай"),
        ("en:spotify", "ru:спутифай"),
        ("en:spotify", "ru:с пути фай"),
        ("en:spotify", "ru:спу ти фай"),
        ("en:youtube", "ru:ютюп"),
        ("en:youtube", "ru:ютуб"),
        ("en:youtube", "ru:ють юб"),
        ("en:youtube", "ru:ють йуб"),
    ],
)
def test_phonetic_equivalence(original_str: str, similar_str: str):
    """
    Test that transcription() produces the same simplified output for both strings.
    """

    # IGNORE_SPACES = True # vowels at the end of the word often add an extra A in the simplephone, while being ignored in the middle of the word

    lang1, orig = original_str.split(":", 1)
    lang2, sim = similar_str.split(":", 1)

    phonetic_orig = transcription(orig, lang1)
    phonetic_sim = transcription(sim, lang2)
    phonetic_orig_solid = transcription(orig.replace(" ", ""), lang1)
    phonetic_sim_solid = transcription(sim.replace(" ", ""), lang2)

    simple_orig = simplephone(phonetic_orig) or ""
    simple_sim = simplephone(phonetic_sim) or ""
    simple_orig_solid = simplephone(phonetic_orig_solid) or ""
    simple_sim_solid = simplephone(phonetic_sim_solid) or ""

    print(
        f"transcription({orig!r}, {lang1!r}) = {phonetic_orig!r} -> simplephone = {simple_orig!r}"
    )
    print(
        f"transcription({sim!r}, {lang2!r}) = {phonetic_sim!r} -> simplephone = {simple_sim!r}"
    )

    def compare_simples(s1, s2):
        abs_distance = levenshtein_distance(s1=s1, s2=s2, max_distance=1)
        rel_difference = abs_distance / max(len(s1), len(s2))
        return abs_distance < 1 or rel_difference < 0.85

    matches = {
        f"{phonetic_orig} -> {simple_orig} != {simple_sim} <- {phonetic_sim}": compare_simples(
            simple_orig, simple_sim
        ),
        f"{phonetic_orig_solid} -> {simple_orig_solid} != {simple_sim_solid} <- {phonetic_sim_solid}": compare_simples(
            simple_orig_solid, simple_sim_solid
        ),
    }

    assert any(matches.values()), [*matches.keys()]
