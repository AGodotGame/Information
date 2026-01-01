import re
import json
from pathlib import Path
from html import escape
from datetime import datetime, date
from zoneinfo import ZoneInfo

H2_RE = re.compile(r"^##\s+(.*)\s*$")
TASK_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.*)$")
DATE_RE = re.compile(r"@\{(\d{4}-\d{2}-\d{2})\}")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(\|([^\]]+))?\]\]")
OBSIDIAN_COMMENT_RE = re.compile(r"%%.*?%%", flags=re.S)

_TAG_COLORS = None


def _norm_tag(tag: str) -> str:
    return tag.strip().lstrip("#").upper()


def _load_tag_colors() -> dict:
    global _TAG_COLORS
    if _TAG_COLORS is not None:
        return _TAG_COLORS

    hooks_dir = Path(__file__).resolve().parent
    cfg_path = hooks_dir / "tag_colors.json"

    raw = {"__default__": {"bg": "#8080801a", "fg": "#cfcfcf"}}

    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                raw.update(data)
        except Exception:
            pass

    normalized = {}
    for k, v in raw.items():
        if not isinstance(v, dict):
            continue
        key = "__default__" if k == "__default__" else _norm_tag(k)
        normalized[key] = v

    normalized.setdefault("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"})

    _TAG_COLORS = normalized
    return normalized


def _tag_style(tag_colors: dict, tag: str) -> str:
    cfg = tag_colors.get(_norm_tag(tag), tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
    bg = cfg.get("bg", "#8080801a")
    fg = cfg.get("fg", "#cfcfcf")
    return f"background-color: {bg}; color: {fg}; border-color: {fg};"


def _strip_obsidian_comments(md: str) -> str:
    return re.sub(OBSIDIAN_COMMENT_RE, "", md)


def _strip_kanban_settings(md: str) -> str:
    md = re.sub(r"%%\s*kanban:settings.*?%%", "", md, flags=re.S | re.I)
    md = re.sub(r"```.*?kanban:settings.*?```", "", md, flags=re.S | re.I)
    return md


def _wikilinks_to_text(s: str) -> str:
    return re.sub(WIKILINK_RE, lambda m: (m.group(3) or m.group(1)), s)


def _extract_dates(text: str):
    dates = DATE_RE.findall(text)
    text = DATE_RE.sub("", text)
    return [d.strip() for d in dates], text.strip()


def _extract_tags(text: str):
    tags = re.findall(r"(?<!\w)#([\w\-_/]+)", text)
    text = re.sub(r"(?<!\w)#[\w\-_/]+", "", text).strip()
    return tags, text


def _parse_date(d: str) -> date | None:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def _today_madrid() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def _date_status(due: date, today: date) -> str:
    if due < today:
        return "past"
    delta = (due - today).days
    if delta < 7:
        return "soon"
    return "later"


def _is_obsidian_kanban_board(markdown: str, page_meta: dict) -> bool:
    if (page_meta or {}).get("kanban-plugin") == "board":
        return True
    head = "\n".join(markdown.splitlines()[:30]).lower()
    return "kanban-plugin:" in head and "board" in head


def on_page_markdown(markdown, page, config, files, **kwargs):
    meta = getattr(page, "meta", {}) or {}
    if not _is_obsidian_kanban_board(markdown, meta):
        return markdown

    tag_colors = _load_tag_colors()
    today = _today_madrid()

    md = _strip_kanban_settings(_strip_obsidian_comments(markdown))

    columns = []
    current = None

    for line in md.splitlines():
        h = H2_RE.match(line)
        if h:
            current = {"title": h.group(1).strip(), "cards": []}
            columns.append(current)
            continue

        if not current:
            continue

        t = TASK_RE.match(line)
        if t:
            done = t.group(1).strip().lower() == "x"
            raw = _wikilinks_to_text(t.group(2).strip())

            dates, rest = _extract_dates(raw)
            tags, title = _extract_tags(rest)
            title = title.strip(" -") or "(sin título)"

            # Un chip por fecha, cada uno con su color
            date_items = []
            for ds in dates:
                d = _parse_date(ds)
                status = _date_status(d, today) if d else None
                date_items.append((ds, status))

            current["cards"].append({
                "done": done,
                "title": title,
                "date_items": date_items,  # [(date_str, past/soon/later)]
                "tags": tags,
            })

    if not columns:
        return markdown

    out = []
    out.append('<div class="kb-board">')

    for col in columns:
        out.append('<section class="kb-col">')
        out.append(f'<header class="kb-col-title">{escape(col["title"])}</header>')
        out.append('<div class="kb-cards">')

        if not col["cards"]:
            out.append('<div class="kb-empty">—</div>')

        for c in col["cards"]:
            done_cls = " kb-done" if c["done"] else ""
            out.append(f'<article class="kb-card{done_cls}">')
            out.append(f'<div class="kb-card-title">{escape(c["title"])}</div>')

            chips = []

            # Fechas: cada @{...} => chip independiente
            for ds, st in c["date_items"]:
                cls = f"kb-chip kb-date {st}" if st else "kb-chip kb-date"
                chips.append(f'<span class="{cls}">{escape(ds)}</span>')

            # Tags con bg+fg desde JSON
            for tag in c["tags"]:
                style = _tag_style(tag_colors, tag)
                chips.append(f'<span class="kb-chip kb-tag" style="{style}">#{escape(tag)}</span>')

            if chips:
                out.append('<div class="kb-meta">' + "".join(chips) + "</div>")

            out.append("</article>")

        out.append("</div></section>")

    out.append("</div>")

    # IMPORTANTE: no devolvemos markdown original para que no se duplique
    return "\n".join(out)
