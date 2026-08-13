/*
 * Live GitHub directory tree.
 *
 * Renders <div class="gh-tree" data-repo="owner/name" data-ref="master"
 * data-path="examples" data-root-dirs-only="1"> as a browsable, lazy-loaded tree:
 *   - directories list their contents via the GitHub Contents API on first expand
 *     (1 request each; the API is CORS-enabled but rate-limited to 60/hr per IP
 *     unauthenticated — laziness keeps calls minimal, and any failure degrades to a
 *     "Browse on GitHub" link).
 *   - files fetch their raw content (raw.githubusercontent.com, no rate limit) on
 *     first expand and highlight via highlight.js if present.
 *
 * Hooks Material's `document$` so it re-runs after instant-navigation page swaps.
 */
(function () {
  var API = "https://api.github.com/repos/";

  function highlight(code) {
    if (window.hljs) {
      try {
        window.hljs.highlightElement(code);
      } catch (e) {
        /* leave plain */
      }
    }
  }

  function makeFile(repo, ref, entry) {
    var det = document.createElement("details");
    det.className = "gh-tree-file";
    var sum = document.createElement("summary");
    sum.textContent = "📄 " + entry.name;
    det.appendChild(sum);
    var body = document.createElement("div");
    det.appendChild(body);

    var loaded = false;
    det.addEventListener("toggle", function () {
      if (!det.open || loaded) return;
      loaded = true;
      var lang = entry.name.indexOf(".") >= 0 ? entry.name.split(".").pop() : "";
      body.innerHTML = '<pre><code class="language-' + lang + '">Loading…</code></pre>';
      var code = body.querySelector("code");
      var raw =
        entry.download_url ||
        "https://raw.githubusercontent.com/" + repo + "/" + ref + "/" + entry.path;
      fetch(raw)
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.text();
        })
        .then(function (t) {
          code.textContent = t;
          highlight(code);
        })
        .catch(function () {
          body.innerHTML =
            '<p><a href="' + entry.html_url + '" target="_blank" rel="noopener">View on GitHub ↗</a></p>';
        });
    });
    return det;
  }

  function makeDir(repo, ref, entry) {
    var det = document.createElement("details");
    det.className = "gh-tree-dir";
    var sum = document.createElement("summary");
    sum.textContent = "📁 " + entry.name + "/";
    det.appendChild(sum);
    var kids = document.createElement("div");
    kids.className = "gh-tree-children";
    det.appendChild(kids);

    var loaded = false;
    det.addEventListener("toggle", function () {
      if (!det.open || loaded) return;
      loaded = true;
      loadInto(kids, repo, ref, entry.path, false);
    });
    return det;
  }

  function loadInto(container, repo, ref, path, dirsOnly) {
    container.innerHTML = '<p class="gh-tree-loading">Loading ' + path + "…</p>";
    fetch(API + repo + "/contents/" + path + "?ref=" + ref)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (items) {
        if (!Array.isArray(items)) throw new Error("not a directory");
        items.sort(function (a, b) {
          if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
          return a.name.localeCompare(b.name);
        });
        container.innerHTML = "";
        items.forEach(function (it) {
          if (it.type === "dir") container.appendChild(makeDir(repo, ref, it));
          else if (!dirsOnly) container.appendChild(makeFile(repo, ref, it));
        });
      })
      .catch(function () {
        container.innerHTML =
          '<p>Couldn\'t list this folder (the GitHub API may be rate-limited). ' +
          '<a href="https://github.com/' +
          repo +
          "/tree/" +
          ref +
          "/" +
          path +
          '" target="_blank" rel="noopener">Browse on GitHub ↗</a></p>';
      });
  }

  function render(el) {
    if (el.dataset.ghDone === "1") return;
    el.dataset.ghDone = "1";
    loadInto(
      el,
      el.getAttribute("data-repo"),
      el.getAttribute("data-ref") || "master",
      el.getAttribute("data-path"),
      el.getAttribute("data-root-dirs-only") === "1"
    );
  }

  function renderAll() {
    document.querySelectorAll(".gh-tree").forEach(render);
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(renderAll);
  } else {
    document.addEventListener("DOMContentLoaded", renderAll);
  }
})();
