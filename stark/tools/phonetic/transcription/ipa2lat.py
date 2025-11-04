import warnings

_mapping = {
    # Vowels
    "i": "i",
    "y": "i",
    "ɨ": "i",
    "ʉ": "u",
    "ɯ": "u",
    "u": "u",
    "ɪ": "i",
    "ʏ": "i",
    "ʊ": "u",
    "e": "e",
    "ø": "e",
    "ɘ": "e",
    "ɵ": "o",
    "ɤ": "o",
    "o": "o",
    "ə": "e",
    "ɛ": "e",
    "œ": "e",
    "ɜ": "e",
    "ɞ": "e",
    "ʌ": "a",
    "ɔ": "o",
    "æ": "a",
    "ɐ": "a",
    "a": "a",
    "ɶ": "a",
    "ä": "a",
    "ɑ": "a",
    "ɒ": "o",
    # Pulmonic Consonants
    "p": "p",
    "b": "b",
    "t": "t",
    "d": "d",
    "ʈ": "t",
    "ɖ": "d",
    "c": "k",
    "ɟ": "j",
    "k": "k",
    "g": "g",
    "q": "k",
    "ɢ": "g",
    "ɡ": "g",
    "m": "m",
    "ɱ": "m",
    "n": "n",
    "ɳ": "n",
    "ɲ": "nj",
    "ŋ": "ng",
    "ʋ": "v",
    "ɹ": "r",
    "ɻ": "r",
    "j": "j",
    "ɰ": "w",
    "ʙ": "b",
    "r": "r",
    "ʀ": "r",
    "ɾ": "r",
    "ɸ": "f",
    "β": "v",
    "f": "f",
    "v": "v",
    "θ": "th",
    "ð": "dh",
    "s": "s",
    "z": "z",
    "ʃ": "sh",
    "ʒ": "zh",
    "ʂ": "sh",
    "ʐ": "zh",
    "ç": "h",
    "ʝ": "j",
    "x": "h",
    "ʑ": "z",
    "ɣ": "gh",
    "χ": "h",
    "ʁ": "gh",
    "ħ": "h",
    "ʕ": "a",
    "h": "h",
    # Clicks
    "ʘ": "o",
    "ǀ": "l",
    "ǃ": "!",
    "ǂ": "!",
    "ǁ": "l",
    # Implosives and Ejectives
    "ɓ": "b",
    "ɗ": "d",
    "ʄ": "j",
    "ɠ": "g",
    "ʛ": "g",
    # Suprasegmentals
    "ˈ": "",
    "ˌ": "",
    "ː": "",
    "ˑ": "",
    "|": "",
    "‖": "",
    ".": "",
    "ʼ": "",
    # Tones and word accents
    "̋": "",
    "́": "",
    "̄": "",
    "̀": "",
    "̏": "",
    "̌": "",
    "̂": "",
    "᷄": "",
    "᷅": "",
    "᷈": "",
    "᷉": "",
    # Other symbols and diacritics
    "ʲ": "",
    "ʷ": "w",
    "ʱ": "h",
    "ʰ": "h",
    "ʴ": "r",
    "ʳ": "r",
    "ˠ": "g",
    "ʡ": "a",
    "ʢ": "a",
    "ɭ": "l",
    "_": "",
    '"': "",
    " ": "",
}


def ipa2lat(ipa_string: str) -> str:
    """Convert IPA string to a simplified Latin string"""

    if not ipa_string:
        return ""

    string = ipa_string[:]
    for ipa, simple in _mapping.items():
        string = string.replace(ipa, simple)

    for symbol in string:
        if symbol not in "abcdefghijklmnopqrstuvwxyz":
            warnings.warn(
                f'ipa2lat: Unknown symbol: "{symbol}" in {string} ({ipa_string})'
            )

    return string
