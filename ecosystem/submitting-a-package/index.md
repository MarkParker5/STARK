# Submitting a Package

Add a package to STARK-PLACE with a pull request. Fork the repo, branch off **`develop`** (always the base), then:

1. **Create the package** — `packages/<name>/` with a `pyproject.toml` and a `stark_<name>/__init__.py`.

1. **Register it in the workspace** — add one line to the root `pyproject.toml`:

   ```toml
   [tool.uv.sources]
   stark-<name> = { workspace = true }
   ```

1. **Re-lock** — `uv lock`.

1. **Add it to CI** — a matrix line in `.github/workflows/test.yml`:

   ```yaml
   - { package: stark-<name>, dir: packages/<name> }
   ```

1. **Open the PR** against `develop`. The package's test + build must pass; a maintainer merges.

Minimal `packages/<name>/pyproject.toml`:

```toml
[project]
name = "stark-<name>"
version = "0.1.0"
description = "…"
license = { text = "PolyForm-Noncommercial-1.0.0" }
requires-python = ">=3.11"
dependencies = ["stark-engine>=4.6,<5"]   # only if it uses the engine

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["stark_<name>"]
```

## Conventions

- Distribution name `stark-<name>`, import name `stark_<name>`. The name must stay unambiguous with "place" dropped.
- Licensed under PolyForm Noncommercial 1.0.0 (same as the engine).
- Add `tests/` if you can — "no tests" counts as a pass, but coverage helps.

After merge, the next release **auto-discovers** your package, builds, tests, tags, and publishes it, and adds it to the [Package Registry](https://stark.markparker.me/ecosystem/package-registry/index.md). No manual release step.

## Contribution License Grant

Opening a pull request means agreeing to this grant (the PR template has a checkbox you must tick):

> By submitting a contribution (pull request) to STARK-PLACE, you certify you have the right to do so, and you grant Mark Parker a perpetual, worldwide, non-exclusive, irrevocable, royalty-free license to use, reproduce, modify, adapt, publish, sublicense, relicense, distribute, repackage, and commercially exploit your contribution and derivative works, in whole or in part, in any medium. You retain copyright to your contribution.

This intentionally grants rights beyond the project's [PolyForm Noncommercial](https://github.com/MarkParker5/STARK-PLACE/tree/master/LICENSE.md) license, so contributed code can be maintained and distributed without per-contributor sign-off.
