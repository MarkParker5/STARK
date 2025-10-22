import warnings


from stark.tools.phonetic import espeak_ng


def phonetic(string: str, language_code: str):
    """
    Converts a string to simplified latin transcription via phonetic (ipa) transliteration.
    """
    return " ".join(ipa2lat(to_ipa(word, language_code)) for word in string.split())


def to_ipa(string: str, language_code: str) -> str:
    return to_ipa__espeak_bin(string, language_code)


def ipa2lat(ipa_string: str) -> str:
    """Converts IPA to a simplified latin transcription."""
    return ipa2lat__dict(ipa_string)


# ----- Implementations: -----

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


def ipa2lat__dict(ipa_string: str) -> str:
    if not ipa_string:
        return ""

    string = ipa_string[:]
    for ipa, simple in _mapping.items():
        string = string.replace(ipa, simple)

    for symbol in string:
        if symbol not in "abcdefghijklmnopqrstuvwxyz":
            warnings.warn(
                f'SuggestionsManager._ipa_to_latin: Unknown symbol: "{symbol}" in {string} ({ipa_string})'
            )

    return string


def to_ipa__espeak_bin(string: str, language_code: str) -> str:
    return espeak_ng.text_to_ipa(string, language_code)


# def to_ipa__espeak_cli(string: str, language_code: str) -> str:
#     import re
#     import subprocess

#     result = subprocess.run(
#         ["espeak-ng", "--ipa", f"-v{language_code}", "-q", string],
#         capture_output=True,
#         text=True,
#     )
#     return re.compile(r"\(.*?\)").sub("", result.stdout.strip()).strip()


# @lru_cache
# def _epitran_obj(language_code: str) -> Epitran:
#     from epitran import Epitran

#     return Epitran(language_code)  # this one is long, about an entire second


# def to_ipa__epitran(string: str, language_code: str) -> str:
#     # if language_code.startswith("en"):
#     #     raise NotImplementedError(
#     #         "IPA to Epitran conversion for English is not implemented yet."
#     #     )

#     if language_code == "ru":
#         language_code = "rus-Cyrl"

#     # Code:	Language (Script)
#     supported_languages = {
#         "aar-Latn": "Afar",
#         "afr-Latn": "Afrikanns",
#         "aii-Syrc": "Assyrian Neo-Aramaic",
#         "amh-Ethi": "Amharic",
#         "amh-Ethi-pp": "Amharic (more phonetic)",
#         "amh-Ethi-red": "Amharic (reduced)",
#         "ara-Arab": "Literary Arabic",
#         "ava-Cyrl": "Avaric",
#         "aze-Cyrl": "Azerbaijani (Cyrillic)",
#         "aze-Latn": "Azerbaijani (Latin)",
#         "ben-Beng": "Bengali",
#         "ben-Beng-red": "Bengali (reduced)",
#         "ben-Beng-east": "East Bengali",
#         "bho-Deva": "Bhojpuri",
#         "bxk-Latn": "Bukusu",
#         "cat-Latn": "Catalan",
#         "ceb-Latn": "Cebuano",
#         "ces-Latn": "Czech",
#         "cjy-Latn": "Jin (Wiktionary)",
#         "ckb-Arab": "Sorani",
#         "cmn-Hans": "Mandarin (Simplified)*",
#         "cmn-Hant": "Mandarin (Traditional)*",
#         "cmn-Latn": "Mandarin (Pinyin)*",
#         "csb-Latn": "Kashubian",
#         "deu-Latn": "German",
#         "deu-Latn-np": "German†",
#         "deu-Latn-nar": "German (more phonetic)",
#         "eng-Latn": "English‡",
#         "epo-Latn": "Esperanto",
#         "est-Latn": "Estonian",
#         "fas-Arab": "Farsi (Perso-Arabic)",
#         "fin-Latn": "Finnish",
#         "fra-Latn": "French",
#         "fra-Latn-np": "French†",
#         "fra-Latn-p": "French (more phonetic)",
#         "ful-Latn": "Fulah",
#         "gan-Latn": "Gan (Wiktionary)",
#         "glg-Latn": "Galician",
#         "got-Goth": "Gothic",
#         "got-Latn": "Gothic (Latin)",
#         "hak-Latn": "Hakka (pha̍k-fa-sṳ)",
#         "hat-Latn-bab": "Haitian (Latin-Babel)",
#         "hau-Latn": "Hausa",
#         "hin-Deva": "Hindi",
#         "hmn-Latn": "Hmong",
#         "hrv-Latn": "Croatian",
#         "hsn-Latn": "Xiang (Wiktionary)",
#         "hun-Latn": "Hungarian",
#         "ilo-Latn": "Ilocano",
#         "ind-Latn": "Indonesian",
#         "ita-Latn": "Italian",
#         "jam-Latn": "Jamaican",
#         "jav-Latn": "Javanese",
#         "jpn-Hira": "Japanese (Hiragana)",
#         "jpn-Hira-red": "red	Japanese (Hiragana, reduced)",
#         "jpn-Jpan": "Japanese (Hiragana, Katakana, Kanji)",
#         "jpn-Kana": "Japanese (Katakana)",
#         "jpn-Kana-red": "red	Japanese (Katakana, reduced)",
#         "kat-Geor": "Georgian",
#         "kaz-Cyrl": "Kazakh (Cyrillic)",
#         "kaz-Cyrl-bab": "bab	Kazakh (Cyrillic—Babel)",
#         "kaz-Latn": "Kazakh (Latin)",
#         "kbd-Cyrl": "Kabardian",
#         "khm-Khmr": "Khmer",
#         "kin-Latn": "Kinyarwanda",
#         "kir-Arab": "Kyrgyz (Perso-Arabic)",
#         "kir-Cyrl": "Kyrgyz (Cyrillic)",
#         "kir-Latn": "Kyrgyz (Latin)",
#         "kmr-Latn": "Kurmanji",
#         "kmr-Latn-red": "Kurmanji (reduced)",
#         "kor-Hang": "Korean",
#         "lao-Laoo": "Lao",
#         "lao-Laoo-prereform": "Lao (Before spelling reform)",
#         "lav-Latn": "Latvian",
#         "lez-Cyrl": "Lezgian",
#         "lij-Latn": "Ligurian",
#         "lit-Latn": "Lithuanian",
#         "lsm-Latn": "Saamia",
#         "ltc-Latn-bax": "Middle Chinese (Baxter and Sagart 2014)",
#         "lug-Latn": "Ganda / Luganda",
#         "mal-Mlym": "Malayalam",
#         "mar-Deva": "Marathi",
#         "mlt-Latn": "Maltese",
#         "mon-Cyrl-bab": "Mongolian (Cyrillic)",
#         "mri-Latn": "Maori",
#         "msa-Latn": "Malay",
#         "mya-Mymr": "Burmese",
#         "nan-Latn": "Hokkien (pe̍h-oē-jī)",
#         "nan-Latn-tl": "Hokkien (Tâi-lô)",
#         "nld-Latn": "Dutch",
#         "nya-Latn": "Chichewa",
#         "ood-Latn-alv": "Tohono O'odham (Alvarez–Hale)",
#         "ood-Latn-sax": "Tohono O'odham (Saxton)",
#         "ori-Orya": "Odia",
#         "orm-Latn": "Oromo",
#         "pan-Guru": "Punjabi (Eastern)",
#         "pol-Latn": "Polish",
#         "por-Latn": "Portuguese",
#         "quy-Latn": "Ayacucho Quechua / Quechua Chanka",
#         "ron-Latn": "Romanian",
#         "run-Latn": "Rundi",
#         "rus-Cyrl": "Russian",
#         "sag-Latn": "Sango",
#         "sin-Sinh": "Sinhala",
#         "slv-Latn": "Slovene / Slovenian",
#         "sna-Latn": "Shona",
#         "som-Latn": "Somali",
#         "spa-Latn": "Spanish",
#         "spa-Latn-eu": "Spanish (Iberian)",
#         "sqi-Latn": "Albanian",
#         "sro-Latn": "Sardinian (Campidanese)",
#         "srp-Latn": "Serbian (Latin)",
#         "srp-Cyrl": "Serbian (Cyrillic)",
#         "swa-Latn": "Swahili",
#         "swa-Latn-red": "Swahili (reduced)",
#         "swe-Latn": "Swedish",
#         "tam-Taml": "Tamil",
#         "tam-Taml-red": "Tamil (reduced)",
#         "tel-Telu": "Telugu",
#         "tgk-Cyrl": "Tajik",
#         "tgl-Latn": "Tagalog",
#         "tgl-Latn-red": "Tagalog (reduced)",
#         "tha-Thai": "Thai",
#         "tir-Ethi": "Tigrinya",
#         "tir-Ethi-pp": "Tigrinya (more phonemic)",
#         "tir-Ethi-red": "Tigrinya (reduced)",
#         "tok-Latn": "Toki Pona",
#         "tpi-Latn": "Tok Pisin",
#         "tuk-Cyrl": "Turkmen (Cyrillic)",
#         "tuk-Latn": "Turkmen (Latin)",
#         "tur-Latn": "Turkish (Latin)",
#         "tur-Latn-bab": "Turkish (Latin—Babel)",
#         "tur-Latn-red": "Turkish (reduced)",
#         "ukr-Cyrl": "Ukrainian",
#         "urd-Arab": "Urdu",
#         "uig-Arab": "Uyghur (Perso-Arabic)",
#         "uzb-Cyrl": "Uzbek (Cyrillic)",
#         "uzb-Latn": "Uzbek (Latin)",
#         "vie-Latn": "Vietnamese",
#         "wuu-Latn": "Shanghainese Wu (Wiktionary)",
#         "xho-Latn": "Xhosa",
#         "yor-Latn": "Yoruba",
#         "yue-Latn": "Cantonese (Jyutping)",
#         "yue-Hant": "Cantonese (Character)",
#         "zha-Latn": "Zhuang",
#         "zul-Latn": "Zulu",
#     }

#     if language_code not in supported_languages:
#         for key in supported_languages:
#             if key.startswith(language_code):
#                 warnings.warn(
#                     f"Unsupported language code: {language_code}; trying to use similar key {key}"
#                 )
#                 language_code = key
#                 break
#         else:
#             raise ValueError(
#                 f"Unsupported language code: {language_code}; supported languages: {supported_languages}"
#             )

#         if not string.strip():
#             return ""

#     return _epitran_obj(language_code).transliterate(string)

if __name__ == "__main__":
    pass
    # print("Starting...")
    # print(to_ipa__epitran("Hello", "eng-Latn"))
    # print("Two more...")
    # print(to_ipa__epitran("Hello", "eng-Latn"))
    # print(to_ipa__epitran("Hello", "eng-Latn"))
    # print("Київ", to_ipa("Київ", "ua"))
    # print("Київ", to_ipa("Київ", "uk"))
    # test_cases = [
    #     'Привет Иван как у тебя делая',
    #     'любимые занятия надо делать часто',
    #     'Съешь ещё этих мягких французских булок да выпей чаю',
    #     'Хай',
    #     'хай',
    #     'Хэллоу',
    #     'хэллоу',
    #     'друг с другом',
    #     'с пути фай',
    # ]
    # for test_case in test_cases:
    #     print((ipa := to_ipa__epitran(test_case, 'rus-Cyrl')), to_ipa__espeak(test_case, 'ru'), ipa2lat__ipapy(ipa), ipa2lat__dict(ipa), sep=' || ')
