from __future__ import annotations

from mkdocs.utils import get_relative_url

import re
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(\|([^\]]+))?\]\]")

# ✅ Cache por build para no recalcular el índice en cada página
_WIKILINK_INDEX_CACHE: dict[int, dict[str, list[dict]]] = {}


def extract_first_wikilink(raw: str):
    """Devuelve (target, label). Si no hay, (None, None)."""
    m = WIKILINK_RE.search(raw or "")
    if not m:
        return None, None
    target = (m.group(1) or "").strip()
    label = (m.group(3) or m.group(1) or "").strip()
    return target, label


def _norm_key(name: str) -> str:
    """
    Normalización “tipo obsidian” (bastante permisiva):
    - lower
    - quita .md
    - colapsa espacios/guiones/underscores
    - quita caracteres raros
    """
    s = (name or "").strip().lower()
    if s.endswith(".md"):
        s = s[:-3]
    s = s.replace("\\", "/")
    s = s.split("/")[-1]  # por si viene con carpeta
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    return s.strip("-")


def _build_wikilink_index(files) -> dict[str, list[dict]]:
    """
    Indexa todas las pages (md) por nombre de fichero.
    Devuelve: key -> [{src_path, url}]
    """
    idx: dict[str, list[dict]] = {}
    try:
        docs = files.documentation_pages()
    except Exception:
        docs = []

    for f in docs:
        src_path = getattr(f, "src_path", None) or getattr(f, "src_uri", None) or ""
        url = getattr(f, "url", None)
        if not url or not src_path:
            continue

        stem = Path(src_path).stem  # "MiTarea"
        key = _norm_key(stem)

        idx.setdefault(key, []).append({"src_path": src_path.replace("\\", "/"), "url": url})

    return idx


def _get_index(files) -> dict[str, list[dict]]:
    """
    Cachea el índice por identidad del objeto `files`.
    """
    k = id(files)
    if k not in _WIKILINK_INDEX_CACHE:
        _WIKILINK_INDEX_CACHE[k] = _build_wikilink_index(files)
    return _WIKILINK_INDEX_CACHE[k]


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

    seen = set()
    ordered = []
    for p in out:
        if p in seen:
            continue
        seen.add(p)
        ordered.append(p)
    return ordered


def _pick_best_match(candidates: list[dict], roots: list[str]) -> dict | None:
    """
    Si hay varias páginas con el mismo nombre, preferimos:
    - que estén dentro de alguno de los roots (research/..., archivados/...)
    - si no, la primera.
    """
    if not candidates:
        return None

    # normalizamos roots para comparar
    roots_norm = [(r.strip().strip("/").lower() + "/") for r in (roots or []) if r.strip().strip("/")]
    if roots_norm:
        for r in roots_norm:
            for c in candidates:
                sp = (c.get("src_path") or "").lower()
                if sp.startswith(r):
                    return c
    return candidates[0]


def resolve_wikilink_href(target: str, page, files, config, roots: list[str]) -> str | None:
    """
    Resuelve [[X]] a url:
    1) intenta por ruta (roots + target.md / target/index.md)
    2) si falla, busca por nombre en todo el sitio (índice), y elige la mejor coincidencia por roots
    """
    if not target:
        return None

    # --- 1) intento por ruta (rápido)
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

    # --- 2) fallback por índice (encuentra research/desarrollos/..., etc.)
    if not file_url:
        idx = _get_index(files)
        key = _norm_key(target)
        matches = idx.get(key, [])
        best = _pick_best_match(matches, roots)
        if best:
            file_url = best["url"]

    # --- 3) fallback convención si todo falla
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
