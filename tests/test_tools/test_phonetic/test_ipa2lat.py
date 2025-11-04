import warnings

from stark.tools.phonetic.transcription import ipa2lat


def test_ipa2lat_basic():
    # Just check that output is non-empty for typical IPA input
    assert ipa2lat("tɛst")
    assert ipa2lat("fuː")
    assert ipa2lat("baːr")
    assert ipa2lat("həlo")


def test_ipa2lat_empty():
    assert ipa2lat("") == ""


def test_ipa2lat_warns_on_unknown():
    # Should warn on unknown symbol (e.g., 'Ω')
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = ipa2lat("Ω")
        assert result == "Ω"
        assert any("Unknown symbol" in str(warn.message) for warn in w)
