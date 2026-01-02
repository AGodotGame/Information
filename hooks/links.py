from __future__ import annotations

from mkdocs.utils import get_relative_url

import re

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(\|([^\]]+))?\]\]")


def extract_first_wikilink(raw: str):
    """Devuelve (target, label). Si no hay, (None, None)."""
    m = WIKILINK_RE.search(raw or "")
    if not m:
        return None, None
    target = (m.group(1) or "").strip()
    label = (m.group(3) or m.group(1) or "").strip()
    return target, label


def candidate_paths_for_target(target: str, roots: list[str]):
    t = (target or "").strip().lstrip("/")
    if not t:
        return []

    base_candidates = []
    if t.lower().endswith(".md"):
        base_candidates.append(t)
    else:
        base_candidates.append(f"{t}.md")
        base_candidates.append(f"{t}/index.md")

    out = []
    for c in base_candidates:
        out.append(c)

    for r in roots or []:
        rr = r.strip().strip("/")
        if not rr:
            continue
        for c in base_candidates:
            out.append(f"{rr}/{c}")

    # de-dupe manteniendo orden
    seen = set()
    ordered = []
    for p in out:
        if p in seen:
            continue
        seen.add(p)
        ordered.append(p)
    return ordered


def resolve_wikilink_href(target: str, page, files, config, roots: list[str]) -> str | None:
    """Resuelve [[X]] contra Files de MkDocs probando roots; devuelve href relativo a page.url."""
    if not target:
        return None

    candidates = candidate_paths_for_target(target, roots)

    file_url = None
    for c in candidates:
        try:
            f = files.get_file_from_path(c)
            if f:
                file_url = getattr(f, "url", None)
                if file_url:
                    break
        except Exception:
            pass

    # fallback por convención
    if not file_url:
        use_dir = bool(config.get("use_directory_urls", True))
        base = target.strip().lstrip("/")
        if base.lower().endswith(".md"):
            base = base[:-3]
        if roots and roots[0]:
            base = f"{roots[0].strip().strip('/')}/{base}".strip("/")
        file_url = base.rstrip("/") + ("/" if use_dir else ".html")

    try:
        return get_relative_url(file_url, page.url)
    except Exception:
        return file_url
