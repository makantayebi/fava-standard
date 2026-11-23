#!/usr/bin/env python3
"""Build the static docs site (site/) for GitHub Pages, from targets.yaml
and the already-committed generated/ diagrams — no new rendering happens
here, this just assembles what render.py already produced into a page.

Usage: python3 tools/gen_docs_site.py
Writes to site/ (gitignored — a GitHub Actions workflow builds and
deploys it on every push; it isn't meant to be committed).
"""
import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = SITE / "assets"


def latest_base_version():
    versions = sorted(
        (ROOT / "versions").iterdir(),
        key=lambda p: [int(x) for x in p.name.lstrip("v").split(".")],
    )
    return versions[-1].name


def copy_svg(src, dest_name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    dest = ASSETS / dest_name
    shutil.copy(src, dest)
    return f"assets/{dest_name}"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_notice_from_yaml(note):
    # targets.yaml's ">" block scalars fold newlines into spaces, like prose.
    return esc(" ".join(note.split()))


def main():
    SITE.mkdir(parents=True, exist_ok=True)
    if ASSETS.exists():
        shutil.rmtree(ASSETS)

    targets_doc = yaml.safe_load((ROOT / "targets.yaml").read_text(encoding="utf-8"))
    targets = targets_doc["targets"]

    base_version = latest_base_version()
    base_svg_src = ROOT / "versions" / base_version / "generated" / "layout.svg"
    base_svg = copy_svg(base_svg_src, f"base-{base_version}.svg") if base_svg_src.exists() else None

    target_sections = []
    for name, info in targets.items():
        if info.get("status") != "implemented":
            continue
        layout_version = info.get("layout_version") or info.get("script_version")
        version_dir = ROOT / "layouts" / name / f"v{layout_version}"
        generated_dir = version_dir / "generated"
        svg_candidates = ["android_layout.svg", "layout.svg"]
        svg_path = None
        for candidate in svg_candidates:
            p = generated_dir / candidate
            if p.exists():
                svg_path = p
                break
        svg_rel = copy_svg(svg_path, f"{name}-v{layout_version}.svg") if svg_path else None

        version_line = f"layout v{layout_version}"
        if info.get("app_version"):
            version_line += f" &middot; app v{info['app_version']}"
        version_line += f" &middot; forked from script v{info.get('forked_from_script_version', '?')}"

        repo = info.get("repo", name)
        target_sections.append(f"""
    <section class="target">
      <h2>{esc(name)}</h2>
      <p class="meta"><a href="https://github.com/makantayebi/{esc(repo)}">{esc(repo)}</a> &mdash; {version_line}</p>
      <p class="note">{render_notice_from_yaml(info.get("note", ""))}</p>
      {f'<img class="diagram" src="{svg_rel}" alt="{esc(name)} keyboard diagram">' if svg_rel else ""}
    </section>""")

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fava (فاوآیی)</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{
    margin: 0; padding: 40px 20px 80px;
    background: #121214; color: #e6e6e6;
    font-family: -apple-system, "Segoe UI", Tahoma, sans-serif;
    display: flex; justify-content: center;
  }}
  main {{ max-width: 760px; width: 100%; }}
  h1 {{ font-size: 2.2rem; margin-bottom: 4px; }}
  .tagline {{ color: #999; margin-top: 0; }}
  .intro {{ color: #ccc; line-height: 1.6; }}
  .intro a {{ color: #7fd1ff; }}
  section.target {{
    margin-top: 48px; padding-top: 32px; border-top: 1px solid #2a2a2c;
  }}
  h2 {{ text-transform: lowercase; font-size: 1.4rem; margin-bottom: 4px; }}
  .meta {{ color: #999; font-size: 0.9rem; margin-top: 0; }}
  .meta a {{ color: #7fd1ff; text-decoration: none; }}
  .meta a:hover {{ text-decoration: underline; }}
  .note {{ color: #bbb; line-height: 1.6; }}
  .diagram {{ max-width: 100%; margin-top: 16px; border-radius: 8px; }}
  footer {{ margin-top: 64px; color: #666; font-size: 0.85rem; }}
  footer a {{ color: #7fd1ff; }}
</style>
</head>
<body>
<main>
  <h1>Fava (فاوآیی)</h1>
  <p class="tagline">A Persian orthographic-reform keyboard layout</p>
  <p class="intro">
    The source of truth lives in
    <a href="https://github.com/makantayebi/fava-standard">fava-standard</a> —
    a base script (<code>versions/</code>) and per-platform forks
    (<code>layouts/&lt;target&gt;/</code>), each independently versioned.
    This page is generated from that repo's own <code>targets.yaml</code>
    and the diagrams <code>tools/render.py</code> already produces, not
    hand-maintained.
  </p>

  <section class="target">
    <h2>base script</h2>
    <p class="meta">{base_version}</p>
    {f'<img class="diagram" src="{base_svg}" alt="base layout diagram">' if base_svg else ""}
  </section>
  {"".join(target_sections)}

  <footer>
    Generated from <a href="https://github.com/makantayebi/fava-standard">fava-standard</a>
    by <code>tools/gen_docs_site.py</code>.
  </footer>
</main>
</body>
</html>
"""
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {SITE / 'index.html'} ({len(target_sections)} target section(s))")


if __name__ == "__main__":
    main()
