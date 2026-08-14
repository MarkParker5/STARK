# Core Concepts

The pieces every command is built from, regardless of how simple or complex it gets:

- **[Patterns](https://stark.markparker.me/core-concepts/patterns/index.md)**: the syntax for matching what a user says and pulling parameters out of it.
- **[Command Response](https://stark.markparker.me/core-concepts/command-response/index.md)**: what a command returns: text, voice, status, and how to chain into follow-up commands.
- **[Commands Context](https://stark.markparker.me/core-concepts/commands-context/index.md)**: nested menus, follow-ups, and stateful conversations.
- **[Dependency Injection](https://stark.markparker.me/core-concepts/dependency-injection/index.md)**: getting response handlers, language info, and your own dependencies into a command function.

Read them in order if you're new, each builds a bit on the last.

## Terminology

Terms used throughout these docs:

- **NLObject** — the base class for every parsed value type ("NL" for natural language). Subclass it to define a type.
- **Native type** — an NLObject that ships with STARK: `NLWord` (a single word), `NLString` (any run of words).
- **Custom NLObject type** — your own NLObject subclass, with its own `pattern` and optional `did_parse`.
- **Parameter type** — an NLObject type used in a pattern parameter (`$name:Type`), registered via `register_parameter_type`.
- **Union** — an NLObject that matches one of several branch types (`A | B`).
- **`value`** — the payload every NLObject carries: a scalar, a list, or a nested NLObject.
