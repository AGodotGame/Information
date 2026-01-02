from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

from mkdocs.utils import get_relative_url


# =========================================================
# CONFIG
# =========================================================

# Marcador que pondrás dentro de index.md:
# <!-- AUTO:DIRINDEX Development -->
# <!-- AUTO:DIRINDEX Archived -->
DIRINDEX_MARK_RE = re.compile(r"<!--\s*AUTO:DIRINDEX\s+([A-Za-z0-9_\-]+)\s*-->")


# Rutas que deben considerarse dentro de cada “grupo”
GROUP_ROOTS = {
    "Developments": [
        "research/Developments",
        "Developments",
    ],
    "Archived": [
        "research/Archived",
        "Archived",
    ],
}

GROUP_ALIASES = {
    "development": "Developments",
    "developments": "Developments",
    "archived": "Archived",
    "archive": "Archived",
}



# =========================================================
# PARSE HELPERS (tags/fechas/título)
# =========================================================

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
TAG_RE = re.compile(r"(?<!\w)#([\w\-_/]+)")
DATE_RE = re.compile(r"@\{(\d{4}-\d{2}-\d{2})\}")


def _today_madrid() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


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


def _norm_tag(tag: str) -> str:
    return tag.strip().lstrip("#").upper()


def _read_text_safe(abs_path: str) -> str:
    try:
        return Path(abs_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _title_from_md(text: str, fallback: str) -> str:
    m = H1_RE.search(text)
    if m:
        return m.group(1).strip()
    return fallback


# =========================================================
# TAG COLORS (reusa tu JSON si existe)
# =========================================================

def _load_tag_colors() -> dict:
    """
    Intenta cargar tag_colors.json desde:
      - hooks/obsidian_kanban/tag_colors.json
      - hooks/tag_colors.json
    """
    # defaults
    raw = {"__default__": {"bg": "#8080801a", "fg": "#cfcfcf"}}

    here = Path(__file__).resolve().parent  # hooks/dir_index
    candidates = [
        here.parent / "obsidian_kanban" / "tag_colors.json",
        here.parent / "tag_colors.json",
    ]

    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    raw.update(data)
                break
            except Exception:
                pass

    normalized = {}
    for k, v in raw.items():
        if not isinstance(v, dict):
            continue
        key = "__default__" if k == "__default__" else _norm_tag(k)
        normalized[key] = v

    normalized.setdefault("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"})
    return normalized


def _tag_style(tag_colors: dict, tag: str) -> str:
    cfg = tag_colors.get(_norm_tag(tag), tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
    bg = cfg.get("bg", "#8080801a")
    fg = cfg.get("fg", "#cfcfcf")
    return f"background-color: {bg}; color: {fg}; border-color: {fg};"


# =========================================================
# INDEX BUILD
# =========================================================

@dataclass
class Entry:
    title: str
    href: str
    tags_norm: list[str]
    tags_display: list[str]
    dates_iso: list[str]
    statuses: list[str]
    has_dates: bool
    rel_src: str

def _starts_with_any(src_path: str, roots: list[str]) -> bool:
    sp = (src_path or "").replace("\\", "/").strip("/")
    sp_l = sp.lower()
    sp_bound = "/" + sp_l + "/"

    for r in roots:
        rr = (r or "").replace("\\", "/").strip("/")
        if not rr:
            continue
        rr_l = rr.lower()

        # match normal al inicio
        if sp_l == rr_l or sp_l.startswith(rr_l + "/"):
            return True

        # match si hay prefijo extra (ej: "docs/") pero respetando fronteras
        if f"/{rr_l}/" in sp_bound:
            return True

    return False



def _collect_entries(files, page, group_name: str, allowed_tags: set[str], today: date) -> list[Entry]:
    roots = GROUP_ROOTS.get(group_name, [])
    if not roots:
        return []

    out: list[Entry] = []

    for f in files.documentation_pages():
        src_path = getattr(f, "src_path", "") or ""
        abs_src_path = getattr(f, "abs_src_path", "") or ""
        url = getattr(f, "url", None)
        if not url or not src_path or not abs_src_path:
            continue

        sp = src_path.replace("\\", "/").lstrip("/")

        # ✅ SOLO .md
        if not sp.lower().endswith(".md"):
            continue

        # ✅ EXCLUIR index.md (cualquier index.md dentro del árbol)
        if sp.lower().endswith("/index.md"):
            continue

        if not _starts_with_any(sp, roots):
            continue

        # Evitar index.md del propio folder si quieres (opcional)
        if sp.lower().endswith("/index.md"):
            # lo dejamos en el índice si quieres; normalmente NO lo listamos
            continue

        text = _read_text_safe(abs_src_path)
        fallback_title = Path(sp).stem
        title = _title_from_md(text, fallback_title)

        # tags
        tags_raw = TAG_RE.findall(text) or []  # sin '#'
        tags_norm_all = sorted({_norm_tag(t) for t in tags_raw})
        tags_norm = [t for t in tags_norm_all if t in allowed_tags]
        tags_display = [t for t in tags_raw if _norm_tag(t) in allowed_tags]

        # fechas
        dates_iso = [d.strip() for d in DATE_RE.findall(text) or []]
        statuses_set = set()
        for ds in dates_iso:
            d = _parse_date_iso(ds)
            if d:
                statuses_set.add(_date_status(d, today))

        href = get_relative_url(url, page.url)

        out.append(
            Entry(
                title=title,
                href=href,
                tags_norm=tags_norm,
                tags_display=tags_display,
                dates_iso=dates_iso,
                statuses=sorted(statuses_set),
                has_dates=bool(dates_iso),
                rel_src=sp,
            )
        )

    # orden por título
    out.sort(key=lambda e: e.title.lower())
    return out


# =========================================================
# RENDER (CSS/JS + HTML)
# =========================================================

DIRINDEX_STYLE = r"""
<style>
.di-wrap{ margin: .4rem 0 1rem; }

.di-controls{
  display:flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin: .2rem 0 .65rem;
}

.di-field{
  display:flex;
  align-items:center;
  gap: 8px;
  border: 1px solid rgba(0,0,0,.12);
  background: rgba(255,255,255,.75);
  border-radius: 14px;
  padding: .4rem .55rem;
}

[data-md-color-scheme="slate"] .di-field{
  border-color: rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
}

.di-field label{
  font-size: .84rem;
  opacity: .85;
  white-space: nowrap;
}

.di-input,.di-select{
  border: 0;
  outline: none;
  background: transparent;
  color: inherit;
  font-size: .92rem;
  min-width: 170px;
}
.di-select{ min-width: 150px; }

.di-tagbar{
  display:flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: .65rem;
}

/* chips “luz”: apagado por defecto */
.di-tag{
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,.12);
  padding: .18rem .55rem;
  font-size: .84rem;
  background: transparent;
  color: inherit;
  cursor: pointer;
  opacity: .7;
  transition: transform .06s ease, box-shadow .06s ease, opacity .06s ease;
}
[data-md-color-scheme="slate"] .di-tag{
  border-color: rgba(255,255,255,.12);
}
.di-tag:hover{
  opacity: .95;
  box-shadow: 0 6px 16px rgba(0,0,0,.12);
}
.di-tag.is-active{
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(0,0,0,.12);
  background: var(--tg-bg);
  color: var(--tg-fg);
  border-color: var(--tg-fg);
}

.di-list{
  display:flex;
  flex-direction: column;
  gap: 10px;
}

.di-card{
  border: 1px solid rgba(0,0,0,.12);
  background: rgba(255,255,255,.9);
  border-radius: 14px;
  padding: .58rem .72rem;
  text-decoration:none;
  color: inherit;
  display:block;
  transition: transform .08s ease, box-shadow .08s ease;
}
[data-md-color-scheme="slate"] .di-card{
  border-color: rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
}
.di-card:hover{
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(0,0,0,.12);
}

.di-title{
  font-weight: 750;
  margin-bottom: .35rem;
  line-height: 1.22;
}

.di-meta{ display:flex; flex-wrap:wrap; gap: 6px; }

.di-chip{
  font-size:.79rem;
  padding:.1rem .48rem;
  border-radius:999px;
  border:1px solid rgba(0,0,0,.12);
  opacity:.95;
}
[data-md-color-scheme="slate"] .di-chip{
  border-color: rgba(255,255,255,.12);
}

.di-empty{
  opacity:.6;
  text-align:center;
  padding:.9rem 0;
}

.di-hidden{ display:none !important; }
</style>
"""

DIRINDEX_SCRIPT = r"""
<script>
(function(){
  const wrap = document.querySelector('[data-di-wrap="1"]');
  if(!wrap) return;

  const qEl = wrap.querySelector('[data-di-filter="q"]');
  const statusEl = wrap.querySelector('[data-di-filter="status"]');
  const fromEl = wrap.querySelector('[data-di-filter="from"]');
  const toEl = wrap.querySelector('[data-di-filter="to"]');
  const tagBtns = Array.from(wrap.querySelectorAll('[data-di-tag]'));
  const cards = Array.from(wrap.querySelectorAll('.di-card'));
  const empty = wrap.querySelector('[data-di-empty="1"]');

  const activeTags = new Set();

  function norm(s){ return (s||"").toString().trim().toLowerCase(); }

  function parseISO(d){
    if(!d) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
    if(!m) return null;
    return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).getTime();
  }

  function anyDateInRange(dates, fromTs, toTs){
    for(const ds of dates){
      const ts = parseISO(ds);
      if(ts === null) continue;
      if(fromTs !== null && ts < fromTs) continue;
      if(toTs !== null && ts > toTs) continue;
      return true;
    }
    return false;
  }

  function apply(){
    const q = norm(qEl && qEl.value);
    const status = (statusEl && statusEl.value) ? statusEl.value : "";
    const fromTs = fromEl && fromEl.value ? parseISO(fromEl.value) : null;
    const toTs = toEl && toEl.value ? parseISO(toEl.value) : null;

    let visible = 0;

    for(const card of cards){
      const title = norm(card.getAttribute('data-title'));
      const tags = (card.getAttribute('data-tags') || "").split(',').filter(Boolean);
      const dates = (card.getAttribute('data-dates') || "").split(',').filter(Boolean);
      const statuses = (card.getAttribute('data-statuses') || "").split(',').filter(Boolean);
      const hasDates = (card.getAttribute('data-hasdates') || "0") === "1";

      const okTitle = !q || title.includes(q);

      let okTag = true;
      if(activeTags.size > 0){
        okTag = tags.some(t => activeTags.has(t));
      }

      let okDate = true;
      if(status === "nodate"){
        okDate = !hasDates;
      } else if(fromTs !== null || toTs !== null){
        okDate = hasDates && anyDateInRange(dates, fromTs, toTs);
      } else if(status){
        okDate = statuses.includes(status);
      }

      const ok = okTitle && okTag && okDate;
      card.classList.toggle('di-hidden', !ok);
      if(ok) visible++;
    }

    if(empty) empty.style.display = (visible === 0) ? 'block' : 'none';
  }

  tagBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const t = btn.getAttribute('data-di-tag');
      if(!t) return;
      if(activeTags.has(t)){
        activeTags.delete(t);
        btn.classList.remove('is-active');
      } else {
        activeTags.add(t);
        btn.classList.add('is-active');
      }
      apply();
    });
  });

  if(qEl) qEl.addEventListener('input', apply);
  if(statusEl) statusEl.addEventListener('change', apply);
  if(fromEl) fromEl.addEventListener('change', apply);
  if(toEl) toEl.addEventListener('change', apply);

  apply();
})();
</script>
"""


def _render_dir_index(group_name: str, entries: list[Entry], tag_colors: dict, allowed_tags: set[str]) -> str:
    # tags presentes en ese directorio
    present = set()
    for e in entries:
        for t in e.tags_norm:
            present.add(t)

    # chips de tag (apagado por defecto)
    chips = []
    for tg in sorted(present):
        cfg = tag_colors.get(tg, tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
        bg = cfg.get("bg", "#8080801a")
        fg = cfg.get("fg", "#cfcfcf")
        chips.append(
            f'<button type="button" class="di-tag" data-di-tag="{tg}" '
            f'style="--tg-bg:{bg};--tg-fg:{fg};">#{tg}</button>'
        )

    out = []
    out.append(DIRINDEX_STYLE)
    out.append('<div class="di-wrap" data-di-wrap="1">')

    # controles
    out.append('<div class="di-controls">')
    out.append(
        '<div class="di-field">'
        '<label>Nombre</label>'
        '<input class="di-input" type="search" placeholder="Buscar..." data-di-filter="q" />'
        '</div>'
    )
    out.append(
        '<div class="di-field">'
        '<label>Fecha</label>'
        '<select class="di-select" data-di-filter="status">'
        "<option value=''>Estado: Todas</option>"
        "<option value='past'>Vencidas</option>"
        "<option value='soon'>Próx. 7 días</option>"
        "<option value='later'>Más tarde</option>"
        "<option value='nodate'>Sin fechas</option>"
        "</select>"
        "</div>"
    )
    out.append(
        '<div class="di-field">'
        '<label>Desde</label>'
        '<input class="di-input" type="date" data-di-filter="from" />'
        '</div>'
    )
    out.append(
        '<div class="di-field">'
        '<label>Hasta</label>'
        '<input class="di-input" type="date" data-di-filter="to" />'
        '</div>'
    )
    out.append("</div>")  # controls

    if chips:
        out.append('<div class="di-tagbar">' + "".join(chips) + "</div>")

    # listado
    out.append('<div class="di-list">')

    if not entries:
        out.append('<div class="di-empty">—</div>')
    else:
        for e in entries:
            data_title = e.title.replace('"', "&quot;")
            data_tags = ",".join(e.tags_norm).replace('"', "&quot;")
            data_dates = ",".join(e.dates_iso).replace('"', "&quot;")
            data_statuses = ",".join(e.statuses).replace('"', "&quot;")
            data_has = "1" if e.has_dates else "0"

            out.append(
                f'<a class="di-card" href="{e.href}"'
                f' data-title="{data_title}"'
                f' data-tags="{data_tags}"'
                f' data-dates="{data_dates}"'
                f' data-statuses="{data_statuses}"'
                f' data-hasdates="{data_has}">'
            )
            out.append(f'<div class="di-title">{e.title}</div>')

            meta = []

            # muestra 1 fecha (si hay)
            if e.dates_iso:
                meta.append(f'<span class="di-chip">{e.dates_iso[0]}</span>')

            # tags (en tarjeta sí con color, para informar)
            for t in e.tags_display:
                meta.append(f'<span class="di-chip" style="{_tag_style(tag_colors, t)}">#{t}</span>')

            if meta:
                out.append('<div class="di-meta">' + "".join(meta) + "</div>")

            out.append("</a>")

        out.append('<div class="di-empty" data-di-empty="1" style="display:none;">Sin resultados</div>')

    out.append("</div>")  # list
    out.append(DIRINDEX_SCRIPT)
    out.append("</div>")  # wrap
    return "\n".join(out)


# =========================================================
# MKDOCS HOOK
# =========================================================

def on_page_markdown(markdown, page, config, files, **kwargs):
    """
    Reemplaza el marcador <!-- AUTO:DIRINDEX X --> por un listado+buscador
    de los MD dentro de research/X (sin necesidad de que estén en nav).
    """
    m = DIRINDEX_MARK_RE.search(markdown or "")
    if not m:
        return markdown
            
    group_raw = m.group(1).strip()
    group = GROUP_ALIASES.get(group_raw.lower(), group_raw)

    if group not in GROUP_ROOTS:
        return markdown


    tag_colors = _load_tag_colors()
    allowed_tags = {k for k in tag_colors.keys() if k != "__default__"}

    today = _today_madrid()
    entries = _collect_entries(files, page, group, allowed_tags, today)

    html = _render_dir_index(group, entries, tag_colors, allowed_tags)

    # Reemplaza solo el primer marcador encontrado
    return DIRINDEX_MARK_RE.sub(lambda _: html, markdown, count=1)
