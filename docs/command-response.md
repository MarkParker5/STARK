# Command Response

The `Response` class represents the outcome of processing a command in the S.T.A.R.K. This documentation section will help you understand the various properties of the `Response` class, allowing you to craft detailed and specific responses to user queries.

## Response Properties

### `voice: str`
**Default:** `''`

This string will be converted to speech and played back to the user. If left empty, no vocal response will be given.

### `text: str`
**Default:** `''`

This property provides a textual representation of the response. It can be displayed in an application interface or used for logging.

### `status: ResponseStatus`
**Default:** `ResponseStatus.success`

This property indicates the state or result of the command's processing. It can be any of the following values:

- **none:** No status set.
- **not_found:** Command not recognized or found.
- **failed:** Command processing failed.
- **success:** Command processed successfully.
- **info:** An informational response.
- **error:** An error occurred during command processing.

### `needs_user_input: bool`

**Default:** `False`

This property, when set to `True`, signals that the assistant is actively awaiting additional input from the user. Additionally, if the response is queued for repetition and `needs_user_input` is set to `true`, the repetition will pause following the current response. This pause gives users the opportunity to address or answer any queries posed by the assistant without being interrupted by subsequent repeated messages.

### `commands: list[Command]`

**Default:** `[]`

This property contains a list of commands associated with the response. These commands can serve various purposes, such as providing context, suggesting subsequent actions to the user, or even structuring nested menus. It's often beneficial to utilize this in conjunction with the `needs_user_input` property to create more interactive and guided user experiences.

### `parameters: dict[str, Any]`

**Default:** `{}`

This property holds a dictionary of supplementary data or context useful to the voice assistant or the underlying command processing framework. Examples include specifying a city when inquiring about the weather or denoting a particular room in the context of smart home operations. This feature enables dynamic and contextual interactions, enhancing the overall user experience.

### `id: UUID`

A unique identifier for the response. It gets automatically set when a response is created. For internal usage only.

### `time: datetime`

The timestamp when the response was created. It gets automatically set upon the creation of a new response. For internal usage only.

### `repeat_last: Response`

Static instance of the Response class, that provides a mechanism to reprocess the last given response. If a new response matches the `repeat_last` instance, the voice assistant will process the previous response again.

## Response Handling in the Framework

Responses play a vital role in the user interaction flow. The `VoiceAssistant` class, along with the `CommandsContext`, processes these responses to ensure the user receives accurate and timely feedback.

- **Upon receiving a new response:** The `VoiceAssistant` initially verifies if the response status belongs to its ignore list. If it doesn't, the assistant subsequently evaluates the mode's timeout parameters and, if applicable, appends the response to its collection. For further details on this behavior, refer to the Modes section on the [VoiceAssistant](/voice-assistant) page.

- **Playing the response:** Depending on the assistant's mode, the response may be converted to speech and played back to the user.

- **Repeating responses:** If there has been recent interaction, the assistant may opt to repeat specific responses, ensuring the user is reminded of any ongoing processes or required actions.

This dynamic and flexible system of handling responses ensures that the user experience is interactive and engaging.

---

This documentation is meant to provide a concise overview of the `Response` class and its role within the S.T.A.R.K framework. It's crucial to understand these properties and mechanisms to design a voice assistant that effectively communicates with the user.
