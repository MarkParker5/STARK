# Custom IO & Context Delegate

S.T.A.R.K. ships `VoiceAssistant` as a ready-made IO layer, and subclassing it (see [Voice Assistant & Modes](https://stark.markparker.me/voice-assistant/index.md)) covers most customization needs, overriding a method to hook into an event, like updating a GUI when a response arrives. But if you want a fundamentally different IO layer, a GUI, a Telegram bot, an API, rather than voice at all, `VoiceAssistant` isn't the starting point. `CommandsContextDelegate` is.

## The Protocol

```python
from typing import Protocol, runtime_checkable
from stark.core import Response

@runtime_checkable
class CommandsContextDelegate(Protocol):
    async def commands_context_did_receive_response(self, response: Response):
        pass

    def remove_response(self, response: Response):
        pass
```

This is the protocol `VoiceAssistant` itself implements. `CommandsContext` calls these methods as commands run, `commands_context_did_receive_response` whenever a `Response` is produced, `remove_response` when a response is withdrawn (e.g. via `ResponseHandler.unrespond`, see [Command Response](https://stark.markparker.me/command-response/index.md)). Implementing it directly gives you the same hook `VoiceAssistant` uses, without inheriting any of its voice-specific behavior (modes, timeouts, speech recognition wiring).

## A Minimal Custom Delegate

```python
import sys
import anyio
from stark.core import CommandsContext, CommandsManager, Response

manager = CommandsManager()

@manager.new('hello')
async def hello_command() -> Response:
    return Response('Hello, Stark!')

class TextDelegate:
    async def commands_context_did_receive_response(self, response: Response):
        print(response.text)                            # 1

    def remove_response(self, response: Response):
        pass                                              # 2

async def main():
    async with anyio.create_task_group() as task_group:
        context = CommandsContext(task_group=task_group, commands_manager=manager)
        context.delegate = TextDelegate()                 # 3

        for line in sys.stdin:
            await context.process_string(line.strip())     # 4

anyio.run(main)
```

1. Print every response as it arrives, this is the entire "IO layer" for a basic text interface.
1. No-op here since this minimal example never removes responses; a GUI delegate would use this to take a response off-screen.
1. Assign your delegate to `CommandsContext.delegate`, this is the wiring `run()` does for you when you use the default voice-assistant path.
1. Feed input in however makes sense for your interface, a terminal loop, a GUI event handler, an incoming Telegram message, an HTTP request.

This is the same "your own assembly function" path covered in [How to Run](https://stark.markparker.me/how-to-run/index.md), that page is the better starting point for choosing between `run()`, overrides, and a fully custom delegate like this.

## Triggering Without Voice

If your custom interface starts the assistant on something other than continuous listening, a keyboard shortcut, a button press, an incoming message, see [External Triggers](https://stark.markparker.me/advanced/external-triggers/index.md) for the `Mode.external()` pattern that pairs with this.

## Alternative Interface Ideas

These aren't built-in, they're illustrations of where a custom `CommandsContextDelegate` (paired with a matching input source) fits well, to spark ideas for your own. See [Project Ideas](https://stark.markparker.me/project-ideas/index.md) for more.

### Telegram Bot

This one's a rocket. A STARK assistant reachable from any phone, no app to install, no microphone permissions to grant. Treat incoming messages as input and outgoing messages as the response. Since the delegate, the message handler, and the bot lifecycle all need to share state (the active chat), it's cleaner to encapsulate everything in one class rather than juggle a delegate object and free-floating handler functions:

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from stark.core import CommandsContext, CommandsManager, Response

manager = CommandsManager()
# ... register commands ...

class StarkTelegram:                                                              # 1
    def __init__(self, manager: CommandsManager, task_group, token: str):
        self.context = CommandsContext(task_group=task_group, commands_manager=manager)
        self.context.delegate = self                                              # 2
        self.chat_id = None
        self.app = Application.builder().token(token).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.on_message))

    async def commands_context_did_receive_response(self, response: Response):    # 3
        if self.chat_id is not None:
            await self.app.bot.send_message(chat_id=self.chat_id, text=response.text)

    def remove_response(self, response: Response):                                # 4
        pass

    async def on_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):   # 5
        self.chat_id = update.effective_chat.id
        await self.context.process_string(update.message.text)

    def start(self):                                                              # 6
        self.app.run_polling()

stark_telegram = StarkTelegram(manager, task_group, token='YOUR_BOT_TOKEN')
stark_telegram.start()
```

1. One class owns the whole bot: the delegate, the message handler, and the start/stop lifecycle. No loose functions or module-level globals to wire together.
1. `self` satisfies `CommandsContextDelegate` directly. No separate delegate object needed since the class implements the protocol itself.
1. Sends every response of STARK back to Telegram, whichever chat last messaged the bot. A multi-chat version would key responses by `chat_id` instead of storing a single one, this is the minimal demo version.
1. No-op here, same as the minimal text delegate earlier on this page.
1. Pass all messages from bot to STARK. For personal use, auth by chat_id whitelist might be wanted here.
1. `start()` is the equivalent of `run()`'s blocking call for the voice path. Hand it off to your task group the same way.

Want actual voice messages instead of text? Run a `SpeechSynthesizer` (see [Speech Synthesis](https://stark.markparker.me/tools/speech-synthesis/index.md)) over the response and send the result as a voice note, and a `SpeechRecognizer` (see [Speech Recognition](https://stark.markparker.me/tools/speech-recognition/index.md)) on incoming voice messages for the reverse direction.

### CLI / Terminal

Type instead of speak, read instead of listen. Excellent for debugging, quick testing, or environments without audio. This is what `STARK_VOICE_CLI=1` already gives you on top of `VoiceAssistant`, see [Voice Assistant & Modes](https://stark.markparker.me/voice-assistant/index.md), but a dedicated text-only delegate (like the minimal example above) skips voice entirely instead of layering on top of it.

### GUI

A graphical delegate can show text responses, visualize context state, accept both typed and spoken input, and offer buttons as an alternative to speaking a command. Useful wherever a visual surface adds clarity that voice alone doesn't.

______________________________________________________________________

The canvas of possibilities is vast, bounded mostly by the IO source you wire up. GUI and HTTP-API interfaces aren't built into S.T.A.R.K. yet, see [Roadmap](https://stark.markparker.me/roadmap/index.md) if you want to build one.
