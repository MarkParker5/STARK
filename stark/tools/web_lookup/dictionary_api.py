from dataclasses import dataclass


@dataclass
class WebLookupResult:
    lang: str
    definition: str
    summary: str


async def lookup(word: str, lang: str) -> WebLookupResult | None:
    import aiohttp

    """Lookup a word in the Dictionary API."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                return None
            elif not 200 <= response.status < 300:
                raise RuntimeError(f"Error: {response.status}")
            else:
                response_json = await response.json()

    text = ""

    # short

    r = response_json[0]
    definition = r["meanings"][0]["definitions"][0]
    short = (
        r["word"].lower().capitalize()
        + " ("
        + (r["meanings"][0]["partOfSpeech"].capitalize() if r["meanings"][0]["partOfSpeech"] != "undefined" else "Разговорный")
        + ") — "
        + definition["definition"].lower().capitalize()
        + (". Синонимы: " + ", ".join(definition["synonyms"]) if definition["synonyms"] else "")
    )
    short = short.replace(word[0].lower() + ".", word.lower())
    short = short.replace(word[0].upper() + ".", word.capitalize())

    if lang == "ru":
        short = short.replace("-н.", "-нибудь")
        short = short.replace("потр.", "потребляется")
        short = short.replace("знач.", "значении")

    # long

    for r in response_json:
        text += (
            "\n"
            + r["word"].lower().capitalize()
            + " ("
            + (r["meanings"][0]["partOfSpeech"].capitalize() if r["meanings"][0]["partOfSpeech"] != "undefined" else "Разговорный")
            + ")\n"
        )
        for definition in r["meanings"][0]["definitions"]:
            text += "\t— " + definition["definition"].lower().capitalize()
            if example := definition.get("example"):
                text += "\n\tНапример: " + example
            if synonyms := definition["synonyms"]:
                text += "\n\tСинонимы: " + ", ".join(synonyms) + "."
            if antonyms := definition["antonyms"]:
                text += "\n\tАнтонимы: " + ", ".join(antonyms) + "."
            text += "\n\n"

    return WebLookupResult(lang=lang, definition=text, summary=short)
