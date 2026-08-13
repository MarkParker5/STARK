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

!!! tip "Make it permanent"
    Add the registry to your `pip.conf` / `requirements.txt` so you don't repeat the flag:

    ```txt
    # requirements.txt
    --find-links https://markparker5.github.io/STARK-PLACE/
    stark-ai
    stark-triggers
    ```

## Browse the registry

The registry lists every package, its latest wheel, and older versions (grouped by
release, tagged with their Python and STARK compatibility):

<iframe
  src="https://markparker5.github.io/STARK-PLACE/"
  title="STARK-PLACE package registry"
  loading="lazy"
  style="width:100%;height:640px;border:1px solid var(--md-default-fg-color--lightest);border-radius:.2rem;margin-top:.5rem;">
</iframe>

<p>
  <a class="md-button md-button--primary" href="https://markparker5.github.io/STARK-PLACE/" target="_blank">
    Open the registry ↗
  </a>
</p>
