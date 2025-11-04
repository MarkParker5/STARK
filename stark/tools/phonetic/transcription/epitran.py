from typing import Any
import warnings


class EpitranIpaProvider:
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def _epitran_obj(self, language_code: str) -> Any:
        if language_code not in self._cache:
            from epitran import Epitran

            self._cache[language_code] = Epitran(language_code)
        return self._cache[language_code]

    def to_ipa(self, string: str, language_code: str) -> str:
        # if language_code.startswith("en"):
        #     raise NotImplementedError(
        #         "IPA to Epitran conversion for English is not implemented yet."
        #     )

        if language_code == "ru":
            language_code = "rus-Cyrl"

        # Code:	Language (Script)
        supported_languages = {
            "aar-Latn": "Afar",
            "afr-Latn": "Afrikanns",
            "aii-Syrc": "Assyrian Neo-Aramaic",
            "amh-Ethi": "Amharic",
            "amh-Ethi-pp": "Amharic (more phonetic)",
            "amh-Ethi-red": "Amharic (reduced)",
            "ara-Arab": "Literary Arabic",
            "ava-Cyrl": "Avaric",
            "aze-Cyrl": "Azerbaijani (Cyrillic)",
            "aze-Latn": "Azerbaijani (Latin)",
            "ben-Beng": "Bengali",
            "ben-Beng-red": "Bengali (reduced)",
            "ben-Beng-east": "East Bengali",
            "bho-Deva": "Bhojpuri",
            "bxk-Latn": "Bukusu",
            "cat-Latn": "Catalan",
            "ceb-Latn": "Cebuano",
            "ces-Latn": "Czech",
            "cjy-Latn": "Jin (Wiktionary)",
            "ckb-Arab": "Sorani",
            "cmn-Hans": "Mandarin (Simplified)*",
            "cmn-Hant": "Mandarin (Traditional)*",
            "cmn-Latn": "Mandarin (Pinyin)*",
            "csb-Latn": "Kashubian",
            "deu-Latn": "German",
            "deu-Latn-np": "German†",
            "deu-Latn-nar": "German (more phonetic)",
            "eng-Latn": "English‡",
            "epo-Latn": "Esperanto",
            "est-Latn": "Estonian",
            "fas-Arab": "Farsi (Perso-Arabic)",
            "fin-Latn": "Finnish",
            "fra-Latn": "French",
            "fra-Latn-np": "French†",
            "fra-Latn-p": "French (more phonetic)",
            "ful-Latn": "Fulah",
            "gan-Latn": "Gan (Wiktionary)",
            "glg-Latn": "Galician",
            "got-Goth": "Gothic",
            "got-Latn": "Gothic (Latin)",
            "hak-Latn": "Hakka (pha̍k-fa-sṳ)",
            "hat-Latn-bab": "Haitian (Latin-Babel)",
            "hau-Latn": "Hausa",
            "hin-Deva": "Hindi",
            "hmn-Latn": "Hmong",
            "hrv-Latn": "Croatian",
            "hsn-Latn": "Xiang (Wiktionary)",
            "hun-Latn": "Hungarian",
            "ilo-Latn": "Ilocano",
            "ind-Latn": "Indonesian",
            "ita-Latn": "Italian",
            "jam-Latn": "Jamaican",
            "jav-Latn": "Javanese",
            "jpn-Hira": "Japanese (Hiragana)",
            "jpn-Hira-red": "red	Japanese (Hiragana, reduced)",
            "jpn-Jpan": "Japanese (Hiragana, Katakana, Kanji)",
            "jpn-Kana": "Japanese (Katakana)",
            "jpn-Kana-red": "red	Japanese (Katakana, reduced)",
            "kat-Geor": "Georgian",
            "kaz-Cyrl": "Kazakh (Cyrillic)",
            "kaz-Cyrl-bab": "bab	Kazakh (Cyrillic—Babel)",
            "kaz-Latn": "Kazakh (Latin)",
            "kbd-Cyrl": "Kabardian",
            "khm-Khmr": "Khmer",
            "kin-Latn": "Kinyarwanda",
            "kir-Arab": "Kyrgyz (Perso-Arabic)",
            "kir-Cyrl": "Kyrgyz (Cyrillic)",
            "kir-Latn": "Kyrgyz (Latin)",
            "kmr-Latn": "Kurmanji",
            "kmr-Latn-red": "Kurmanji (reduced)",
            "kor-Hang": "Korean",
            "lao-Laoo": "Lao",
            "lao-Laoo-prereform": "Lao (Before spelling reform)",
            "lav-Latn": "Latvian",
            "lez-Cyrl": "Lezgian",
            "lij-Latn": "Ligurian",
            "lit-Latn": "Lithuanian",
            "lsm-Latn": "Saamia",
            "ltc-Latn-bax": "Middle Chinese (Baxter and Sagart 2014)",
            "lug-Latn": "Ganda / Luganda",
            "mal-Mlym": "Malayalam",
            "mar-Deva": "Marathi",
            "mlt-Latn": "Maltese",
            "mon-Cyrl-bab": "Mongolian (Cyrillic)",
            "mri-Latn": "Maori",
            "msa-Latn": "Malay",
            "mya-Mymr": "Burmese",
            "nan-Latn": "Hokkien (pe̍h-oē-jī)",
            "nan-Latn-tl": "Hokkien (Tâi-lô)",
            "nld-Latn": "Dutch",
            "nya-Latn": "Chichewa",
            "ood-Latn-alv": "Tohono O'odham (Alvarez–Hale)",
            "ood-Latn-sax": "Tohono O'odham (Saxton)",
            "ori-Orya": "Odia",
            "orm-Latn": "Oromo",
            "pan-Guru": "Punjabi (Eastern)",
            "pol-Latn": "Polish",
            "por-Latn": "Portuguese",
            "quy-Latn": "Ayacucho Quechua / Quechua Chanka",
            "ron-Latn": "Romanian",
            "run-Latn": "Rundi",
            "rus-Cyrl": "Russian",
            "sag-Latn": "Sango",
            "sin-Sinh": "Sinhala",
            "slv-Latn": "Slovene / Slovenian",
            "sna-Latn": "Shona",
            "som-Latn": "Somali",
            "spa-Latn": "Spanish",
            "spa-Latn-eu": "Spanish (Iberian)",
            "sqi-Latn": "Albanian",
            "sro-Latn": "Sardinian (Campidanese)",
            "srp-Latn": "Serbian (Latin)",
            "srp-Cyrl": "Serbian (Cyrillic)",
            "swa-Latn": "Swahili",
            "swa-Latn-red": "Swahili (reduced)",
            "swe-Latn": "Swedish",
            "tam-Taml": "Tamil",
            "tam-Taml-red": "Tamil (reduced)",
            "tel-Telu": "Telugu",
            "tgk-Cyrl": "Tajik",
            "tgl-Latn": "Tagalog",
            "tgl-Latn-red": "Tagalog (reduced)",
            "tha-Thai": "Thai",
            "tir-Ethi": "Tigrinya",
            "tir-Ethi-pp": "Tigrinya (more phonemic)",
            "tir-Ethi-red": "Tigrinya (reduced)",
            "tok-Latn": "Toki Pona",
            "tpi-Latn": "Tok Pisin",
            "tuk-Cyrl": "Turkmen (Cyrillic)",
            "tuk-Latn": "Turkmen (Latin)",
            "tur-Latn": "Turkish (Latin)",
            "tur-Latn-bab": "Turkish (Latin—Babel)",
            "tur-Latn-red": "Turkish (reduced)",
            "ukr-Cyrl": "Ukrainian",
            "urd-Arab": "Urdu",
            "uig-Arab": "Uyghur (Perso-Arabic)",
            "uzb-Cyrl": "Uzbek (Cyrillic)",
            "uzb-Latn": "Uzbek (Latin)",
            "vie-Latn": "Vietnamese",
            "wuu-Latn": "Shanghainese Wu (Wiktionary)",
            "xho-Latn": "Xhosa",
            "yor-Latn": "Yoruba",
            "yue-Latn": "Cantonese (Jyutping)",
            "yue-Hant": "Cantonese (Character)",
            "zha-Latn": "Zhuang",
            "zul-Latn": "Zulu",
        }

        if language_code not in supported_languages:
            for key in supported_languages:
                if key.startswith(language_code):
                    warnings.warn(
                        f"Unsupported language code: {language_code}; trying to use similar key {key}"
                    )
                    language_code = key
                    break
            else:
                raise ValueError(
                    f"Unsupported language code: {language_code}; supported languages: {supported_languages}"
                )

            if not string.strip():
                return ""

        return self._epitran_obj(language_code).transliterate(string)
