"""MkDocs hook: append the live STARK-PLACE registry + examples tree to llms.txt.

The registry (an iframe) and examples (a client-side gh-tree) render at view time, so
the llmstxt plugin — which reads page markdown — captures none of their content. This
hook fetches both from GitHub at build and appends a static section to the generated
llms.txt / llms-full.txt. Network failures degrade to a note; they never fail the build.
"""

import json
import urllib.request

REPO = "MarkParker5/STARK-PLACE"
REF = "master"
FIND_LINKS = "https://markparker5.github.io/STARK-PLACE/"
TIMEOUT = 15


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "stark-docs"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def _registry_md():
    releases = _get(f"https://api.github.com/repos/{REPO}/releases")
    latest = {}  # package -> version, from tags like "stark-ai-v0.1.0"
    for rel in releases:
        tag = rel.get("tag_name", "")
        if "-v" not in tag:
            continue
        pkg, ver = tag.rsplit("-v", 1)
        latest.setdefault(pkg, ver)  # releases are newest-first
    if not latest:
        return None
    lines = [
        "## STARK-PLACE Package Registry",
        "",
        f"Self-hosted `--find-links` index: {FIND_LINKS}",
        "Install: `pip install <package> --find-links " + FIND_LINKS + "`",
        "",
    ]
    for pkg in sorted(latest):
        lines.append(f"- {pkg} {latest[pkg]}")
    return "\n".join(lines)


def _examples_md():
    tree = _get(f"https://api.github.com/repos/{REPO}/git/trees/{REF}?recursive=1").get("tree", [])
    paths = sorted(
        n["path"] for n in tree if n.get("type") == "blob" and n["path"].startswith("examples/")
    )
    if not paths:
        return None
    lines = ["## STARK-PLACE Examples", "", f"Live tree of `examples/` in {REPO} (@{REF}):", ""]
    lines += [f"- {p}" for p in paths]
    return "\n".join(lines)


def on_post_build(config, **kwargs):
    import os

    try:
        blocks = [b for b in (_registry_md(), _examples_md()) if b]
        section = "\n\n" + "\n\n".join(blocks) + "\n" if blocks else (
            "\n\n## STARK-PLACE\nRegistry + examples unavailable at build time; "
            f"see {FIND_LINKS} and https://github.com/{REPO}/tree/{REF}/examples\n"
        )
    except Exception as e:  # noqa: BLE001 — never fail the build over enrichment
        section = (
            f"\n\n## STARK-PLACE\nRegistry + examples unavailable at build time ({e}); "
            f"see {FIND_LINKS} and https://github.com/{REPO}/tree/{REF}/examples\n"
        )

    for name in ("llms.txt", "llms-full.txt"):
        path = os.path.join(config["site_dir"], name)
        if os.path.exists(path):
            with open(path, "a", encoding="utf-8") as f:
                f.write(section)
