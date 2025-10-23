import warnings

from stark.tools.phonetic import ipa


def test_ipa2lat_basic():
    # Just check that output is non-empty for typical IPA input
    assert ipa.ipa2lat("tɛst")
    assert ipa.ipa2lat("fuː")
    assert ipa.ipa2lat("baːr")
    assert ipa.ipa2lat("həlo")


def test_ipa2lat_empty():
    assert ipa.ipa2lat("") == ""


def test_ipa2lat_warns_on_unknown():
    # Should warn on unknown symbol (e.g., 'Ω')
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = ipa.ipa2lat("Ω")
        assert result == "Ω"
        assert any("Unknown symbol" in str(warn.message) for warn in w)
