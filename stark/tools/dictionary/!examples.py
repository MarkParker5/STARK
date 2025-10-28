# Simple Usage

# Startup
dictionary = Dictionary(storage=DictionaryStorageMemory())
dictionary.write_one("Nürnberg", {"coords": (49.45, 11.08)})

# Parsing
matches = dictionary.lookup("Nuremberg")
matches[0].metadata  # {'coords': (49.45, 11.08)}

matches = dictionary.lookup("Нюрнберг")
matches[0].metadata  # {'coords': (49.45, 11.08)}

# Usage via NLDictionaryName Example 1 - plain


class NLExampleDictionaryName(NLDictionaryName):
    dictionary = Dictionary(storage=DictionaryStorageMemory())  # single shared instance
    # NOTE: pattern is **, did_parse is already implemented


NLExampleDictionaryName.dictionary.write_one(
    ...
)  # fill at startup, update in runtime if needed

# After did_parse, .value of such an object will contain sorted list[DictionaryItem] with the closest match first (at least one always exists).
# if len(matches) > 1, you can just take the first, sort it any other way, or ask the user to choose.

# Usage via NLDictionaryName Example 2 - encapsulated in subclass (preferred)


class MyDictionary(Dictionary):
    def __init__(self):
        # encapsulate db path in custom class
        super().__init__(
            storage=DictionaryStorageSQL("sqlite:///my-phonetic-dictionary.db")
        )

    async def build(self):
        # encapsulate filling logic
        # files lookup, db fetch, api requests, etc
        self.write_all(...)


class NLExampleDictionaryName(NLObject):
    dictionary = (
        MyDictionary()
    )  # single shared instance of the custom Dictionary subclass


# main.py with build command example:

import typer

app = typer.Typer()


@app.command()
def build():
    """Build the project. See typer docs for better CLI with features like progress bars and logging."""
    print("Building...")
    NLExampleDictionaryName.dictionary.build()  # fill the sqlite file once during the build stage, not at runtime
    SomeOtherDictionary.build()
    # etc
    print("Done")


@app.command()
def run():
    """Run the project."""
    pass


if __name__ == "__main__":
    app()
