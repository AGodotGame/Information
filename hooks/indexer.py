from __future__ import annotations

import re
from pathlib import Path
from datetime import date
from typing import Iterable

from mkdocs.utils import get_relative_url

# Reutilizamos la misma idea de tags/fechas del kanban
TAG_RE = re.compile(r"(?<!\w)#([\w\-_/]+)")
DATE_RE = re.compile(r"@\{(\d{4}-\d{2}-\d{2})\}")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)

_INDEX_CACHE: dict[int, list[dict]] = {}


def _norm_tag(tag: str) -> str:
    return tag.strip().lstrip("#").upper()


def _read_title_from_md(path: str) -> str | None:
    try:
        txt = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    m = H1_RE.search(txt)
    if m:
        return m.group(1).strip()
    return None


def _extract_tags_from_md(path: str, allowed_tags: set[str] | None) -> tuple[list[str], list[str]]:
    """Devuelve (tags_display, tags_norm_filtradas)."""
    try:
        txt = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return [], []
    raw = TAG_RE.findall(txt) or []
    # raw viene sin #
    tags_norm_all = sorted({_norm_tag(t) for t in raw})
    if allowed_tags is None:
        return raw, tags_norm_all
    tags_norm = [t for t in tags_norm_all if t in allowed_tags]
    tags_display = [t for t in raw if _norm_tag(t) in allowed_tags]
    return tags_display, tags_norm


def _extract_dates_from_md(path: str) -> list[str]:
    try:
        txt = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return [d.strip() for d in DATE_RE.findall(txt) or []]


def _parse_date_iso(ds: str) -> date | None:
    try:
        y, m, d = ds.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def _date_status(due: date, today: date) -> str:
    if due < today:
        return "past"
    delta = (due - today).days
    if delta < 7:
        return "soon"
    return "later"


def _starts_with_any(src_path: str, roots: Iterable[str]) -> bool:
    sp = (src_path or "").replace("\\", "/")
    for r in roots:
        rr = (r or "").strip().strip("/")
        if not rr:
            continue
        if sp.startswith(rr + "/") or sp == rr:
            return True
    return False


def collect_index_entries(
    files,
    page,
    today: date,
    *,
    dev_roots: list[str],
    arch_roots: list[str],
    allowed_tags: set[str] | None,
):
    """
    Devuelve una lista de entries:
    {
      group: "dev"|"arch",
      title,
      href,
      tags_norm,
      tags_display,
      dates_iso,
      statuses,
      has_dates
    }
    """
    cache_key = id(files)
    if cache_key in _INDEX_CACHE:
        # OJO: href depende de page.url -> recalculamos href pero reutilizamos metadatos
        base = _INDEX_CACHE[cache_key]
        out = []
        for e in base:
            out.append({**e, "href": get_relative_url(e["url"], page.url)})
        return out

    base_entries: list[dict] = []

    for f in files.documentation_pages():
        src_path = getattr(f, "src_path", "") or ""
        abs_src_path = getattr(f, "abs_src_path", "") or ""
        url = getattr(f, "url", None)
        if not url or not abs_src_path:
            continue

        sp = src_path.replace("\\", "/")

        group = None
        if _starts_with_any(sp, dev_roots):
            group = "dev"
        elif _starts_with_any(sp, arch_roots):
            group = "arch"
        else:
            continue

        # Título
        title = _read_title_from_md(abs_src_path) or Path(sp).stem

        # Tags (solo las permitidas)
        tags_display, tags_norm = _extract_tags_from_md(abs_src_path, allowed_tags)

        # Fechas (para filtros)
        dates_iso = _extract_dates_from_md(abs_src_path)
        statuses = set()
        for ds in dates_iso:
            d = _parse_date_iso(ds)
            if d:
                statuses.add(_date_status(d, today))

        base_entries.append(
            {
                "group": group,
                "title": title,
                "url": url,  # guardamos url “absoluta” de mkdocs; href se hace relativo al page.url
                "tags_display": tags_display,
                "tags_norm": tags_norm,
                "dates_iso": dates_iso,
                "statuses": sorted(statuses),
                "has_dates": bool(dates_iso),
            }
        )

    # cacheamos base
    _INDEX_CACHE[cache_key] = base_entries

    # devolvemos con href relativo
    out = []
    for e in base_entries:
        out.append({**e, "href": get_relative_url(e["url"], page.url)})
    return out
