Coming Soon

This page describes planned work, not shipped functionality. Nothing about S.T.A.R.K.'s current API or behavior changes because of this. What's below is an optional layer being designed on top.

# Agent Platform

S.T.A.R.K.'s next major release (v5) adds an optional layer for building agents: assistants that don't just respond, they take multi-step action on their own. Here's the early, honest version of that plan.

## What's Changing (and What Isn't)

Nothing about S.T.A.R.K.'s core values changes. Agents are an optional layer built on top of what already exists, not a pivot. The load-bearing pieces are already here:

- **Background commands and async intermediate responses.** See [Sync vs Async Commands](https://stark.markparker.me/sync-vs-async-commands/#background-commands). An agent running a multi-step task and reporting progress as it goes uses the same mechanism as a timer reporting "50% done."
- **LLM integration**, already underway. See [Fallback Command / LLM Integration](https://stark.markparker.me/advanced/fallback-command-llm-integration/index.md).

## What "Agent" Actually Means Here

Stripped of marketing language: an agent is a fallback-style LLM command that, instead of just answering, can take arbitrary actions (running terminal commands, controlling a browser, operating peripherals) wrapped in a loop, so it can take more than one step toward a goal. That's it. A lot of the "agent mode" branding floating around the industry right now is exactly that: branding, applied to a fairly simple loop. We'd rather build that loop on infrastructure that's already proven (background commands, multiple responses) than treat it as some new paradigm bolted on top.

## Design Stance

A few principles guiding the implementation, carried over from how the rest of S.T.A.R.K. is built:

- **Minimize LLM involvement where possible.** Assign models narrow, well-scoped tasks for more deterministic results. The less a request depends on the model getting it right, the more reliable the assistant.
- **Isolate LLM-touched components.** Keep model-driven logic in its own module, separate from deterministic pattern matching. A hallucination should stay contained, not corrupt the rest of the pipeline.
- **Keep models swappable.** S.T.A.R.K. is modular. A tiny, sub-billion-parameter on-device model is the right call for simple tasks. A large cloud model is the right call when the task actually needs it. The agent layer shouldn't force a choice between them.

This is consistent with S.T.A.R.K.'s "no AI required, AI is opt-in" position, not a departure from it. Agents are a deeper opt-in, not a new requirement.

## Status

Early planning. The exact shape (structured output, function/tool calling, or something else) is still being weighed against what models reliably support today. If you have opinions on the implementation, or want to help build it, [Discussions](https://github.com/MarkParker5/STARK/discussions) is the place. This direction is genuinely still open.

See also [Roadmap](https://stark.markparker.me/roadmap/index.md) for everything else planned alongside this.
