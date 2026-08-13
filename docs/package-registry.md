# STARK-PLACE Package Registry

STARK-PLACE ships as **several small, independently-installable packages** rather than
one monolith. Each is versioned, tagged, and released on its own; you install only the
ones you need.

The packages are published to a self-hosted **[`--find-links`](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-f)
registry** on GitHub Pages, with the wheels stored as GitHub Release assets:

<p>
  <a class="md-button md-button--primary" href="https://markparker5.github.io/STARK-PLACE/" target="_blank">
    Open the registry ↗
  </a>
</p>

## Packages

| Package | Install name | What it is |
| --- | --- | --- |
| **stark-ai** | `stark-ai` | LLM processors — agentic loop, structured & search parsing, LLM/embedding NER, fallback agent. |
| **stark-triggers** | `stark-triggers` | Input triggers — keyboard hotkey and Porcupine wakeword. |
| **stark-devtools** | `stark-devtools` | Dev tools — `sys.monitoring` profiler + web visualizer (replay, dashboard, wiring, brain). |

Each package imports under its own top-level name (`stark_ai`, `stark_triggers`,
`stark_devtools`) and depends on the engine (`stark-engine`) where relevant.

## Installing

Point pip at the registry with `--find-links`. PyPI is still used for everything else
(including the `stark-engine` core), so normal dependency resolution just works:

```bash
pip install --find-links https://markparker5.github.io/STARK-PLACE/ stark-ai
```

Install several at once:

```bash
pip install --find-links https://markparker5.github.io/STARK-PLACE/ \
  stark-ai stark-triggers stark-devtools
```

!!! tip "Make it permanent"
    Add the registry to your `pip.conf` / `requirements.txt` so you don't repeat the flag:

    ```txt
    # requirements.txt
    --find-links https://markparker5.github.io/STARK-PLACE/
    stark-ai
    stark-triggers
    ```

### Copy what you need

STARK-PLACE is as much a reference collection as a set of packages. For a single command
or module, it's often cleaner to copy the relevant code straight from
[MarkParker5/STARK-PLACE](https://github.com/MarkParker5/STARK-PLACE) into your project
(keeping the attribution comment intact, per the license) than to add a dependency.

## Browse the registry

The registry lists every package, its latest wheel, and older versions (grouped by
release, tagged with their Python and STARK compatibility):

<iframe
  src="https://markparker5.github.io/STARK-PLACE/"
  title="STARK-PLACE package registry"
  loading="lazy"
  style="width:100%;height:640px;border:1px solid var(--md-default-fg-color--lightest);border-radius:.2rem;margin-top:.5rem;">
</iframe>
