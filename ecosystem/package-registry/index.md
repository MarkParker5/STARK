# STARK-PLACE Package Registry

STARK-PLACE ships as several small, independently-installable packages.

## Installing

STARK-PLACE packages are published to a self-hosted **[`--find-links`](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-f) registry**. Use pip as usual but add `--find-links` argument like bellow:

```bash
pip install <stark-package> --find-links https://markparker5.github.io/STARK-PLACE/`
```

For example:

```bash
pip install stark-ai --find-links https://markparker5.github.io/STARK-PLACE/
```

Install several at once:

```bash
pip install stark-ai stark-triggers stark-devtools \ 
    --find-links https://markparker5.github.io/STARK-PLACE/
```

Make it permanent

Add the registry to your `pip.conf` / `requirements.txt` so you don't repeat the flag:

```text
# requirements.txt
--find-links https://markparker5.github.io/STARK-PLACE/
stark-ai
stark-triggers
```

## Browse the registry

The registry lists every package, its latest wheel, and older versions (grouped by release, tagged with their Python and STARK compatibility):

[Open the registry ↗](https://markparker5.github.io/STARK-PLACE/)
