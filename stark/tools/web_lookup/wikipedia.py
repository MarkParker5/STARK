from logging import getLogger

from asyncer import asyncify

logger = getLogger(__name__)


async def lookup(word: str, lang: str) -> str:
    import wikipedia as wiki

    wiki.set_lang(lang)

    try:
        article = await asyncify(wiki.summary)(word, sentences=5)
    except Exception as e:
        logger.error(f"Error: {e}")
        return ""

    try:
        article = article[: article.find("\n\n")]
    except ValueError:
        pass

    summary = ""
    for sentence in article.split("."):
        if len(sentence) < 600:
            summary += sentence.strip() + ". "
        else:
            break

    return summary
