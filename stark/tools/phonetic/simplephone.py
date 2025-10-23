import string


def simplephone(text: str, glue: str = " ", sep: str = string.whitespace) -> str | None:
    """
    Caverphone2 / Soundex / Kölner Phonetik inspired algorithm for phonetic encoding of words.
    No filling with "1", no length limit, skip spaces, return None for empty input.
    """
    return (
        glue.join(simplephone_word(word) or "" for word in text.split()).strip(sep)
        or None
    )


def simplephone_word(word: str) -> str | None:
    # TODO: consider compiling for performance boost
    """
    Caverphone2 / Soundex / Kölner Phonetik inspired algorithm for phonetic encoding of words.
    No filling with "1", no length limit, return None if word is empty.
    """

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    vowels = "aeiou"

    word = word.lower()
    word = "".join(_w for _w in word if _w in alphabet)

    if not word:
        return None

    if word[-1:] == "e":
        word = word[0:-1]

    if word[0:5] == "cough":
        word = "cou2f" + word[5:]
    if word[0:5] == "rough":
        word = "rou2f" + word[5:]
    if word[0:5] == "tough":
        word = "tou2f" + word[5:]
    if word[0:6] == "enough":
        word = "enou2f" + word[5:]
    if word[0:6] == "trough":
        word = "trou2f" + word[5:]
    if word[0:2] == "gn":
        word = "2n" + word[2:]
    if word[-2:] == "mb":
        word = word[0:-2] + "m2"

    word = word.replace("cq", "2q")
    word = word.replace("ci", "si")
    word = word.replace("ce", "se")
    word = word.replace("cy", "sy")
    word = word.replace("tch", "2ch")
    word = word.replace("c", "k")
    word = word.replace("q", "k")
    word = word.replace("x", "k")
    word = word.replace("v", "f")
    word = word.replace("dg", "2g")
    word = word.replace("tio", "sio")
    word = word.replace("tia", "sia")
    word = word.replace("d", "t")
    word = word.replace("ph", "fh")
    word = word.replace("b", "p")
    word = word.replace("sh", "s2")
    word = word.replace("z", "s")

    if word[0:1] in vowels:
        word = "A" + word[1:]
    for _v in vowels:
        word = word.replace(_v, "3")

    word = word.replace("j", "y")
    word = word.replace("y3", "Y3")

    if word[0:2] == "y3":
        word = "Y3" + word[2:]
    if word[0] == "y":
        word = "A" + word[1:]

    word = word.replace("y", "3")
    word = word.replace("3gh3", "3kh3")
    word = word.replace("gh", "22")
    word = word.replace("g", "k")

    for _w in "stpkfmn":
        while _w * 2 in word:
            word = word.replace(_w * 2, _w)
        word = word.replace(_w, _w.upper())

    word = word.replace("w3", "W3")
    word = word.replace("wh3", "Wh3")

    if word[-1:] == "w":
        word = word[0:-1] + "3"

    word = word.replace("w", "2")

    if word[0:1] == "h":
        word = "A" + word[1:]

    word = word.replace("h", "2")
    word = word.replace("r3", "R3")

    if word[-1:] == "r":
        word = word[0:-1] + "3"

    word = word.replace("r", "2")
    word = word.replace("l3", "L3")

    if word[-1:] == "l":
        word = word[0:-1] + "3"

    word = word.replace("l", "2")
    word = word.replace("2", "")

    if word[-1:] == "3":
        word = word[0:-1] + "A"

    word = word.replace("3", "")

    # while len(word) < 10:
    #     word += '1'

    if word == "A":
        return None

    return word
