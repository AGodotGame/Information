from __future__ import annotations

import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

from tag_colors import norm_tag

H2_RE = re.compile(r"^##\s+(.*)\s*$")
TASK_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.*)$")
DATE_RE = re.compile(r"@\{(\d{4}-\d{2}-\d{2})\}")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(\|([^\]]+))?\]\]")
OBSIDIAN_COMMENT_RE = re.compile(r"%%.*?%%", flags=re.S)


def strip_obsidian_comments(md: str) -> str:
    return re.sub(OBSIDIAN_COMMENT_RE, "", md)


def strip_kanban_settings(md: str) -> str:
    md = re.sub(r"%%\s*kanban:settings.*?%%", "", md, flags=re.S | re.I)
    md = re.sub(r"```.*?kanban:settings.*?```", "", md, flags=re.S | re.I)
    return md


def is_obsidian_kanban_board(markdown: str, page_meta: dict) -> bool:
    if (page_meta or {}).get("kanban-plugin") == "board":
        return True
    head = "\n".join(markdown.splitlines()[:30]).lower()
    return "kanban-plugin:" in head and "board" in head


def wikilinks_to_text(s: str) -> str:
    return re.sub(WIKILINK_RE, lambda m: (m.group(3) or m.group(1)), s)


def extract_first_wikilink_target(raw: str) -> str | None:
    m = WIKILINK_RE.search(raw or "")
    if not m:
        return None
    return (m.group(1) or "").strip() or None


def extract_dates(text: str):
    dates = DATE_RE.findall(text)
    text = DATE_RE.sub("", text)
    return [d.strip() for d in dates], text.strip()


def extract_tags(text: str):
    tags = re.findall(r"(?<!\w)#([\w\-_/]+)", text)
    text = re.sub(r"(?<!\w)#[\w\-_/]+", "", text).strip()
    return tags, text


def parse_date(d: str) -> date | None:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def today_madrid() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def date_status(due: date, today: date) -> str:
    if due < today:
        return "past"
    delta = (due - today).days
    if delta < 7:
        return "soon"
    return "later"


def parse_board(
    markdown: str,
    page_meta: dict,
    today: date,
    *,
    allowed_tags: set[str] | None = None,
    archive_keyword: str = "archiv",
):
    """
    Devuelve (columns, all_tags_norm)
    columns: [{title, archived, cards:[...]}]
    card: {done,title,target,href?,date_items,tags,tags_norm,dates_iso,statuses,has_dates}
    """
    if not is_obsidian_kanban_board(markdown, page_meta):
        return [], set()

    md = strip_kanban_settings(strip_obsidian_comments(markdown))

    columns = []
    current = None
    all_tags_norm = set()

    for line in md.splitlines():
        h = H2_RE.match(line)
        if h:
            title = h.group(1).strip()
            is_archived = archive_keyword in title.lower()
            current = {"title": title, "cards": [], "archived": is_archived}
            columns.append(current)
            continue

        if not current:
            continue

        t = TASK_RE.match(line)
        if not t:
            continue

        done = t.group(1).strip().lower() == "x"
        raw_line = t.group(2).strip()

        target = extract_first_wikilink_target(raw_line)

        raw = wikilinks_to_text(raw_line)
        dates, rest = extract_dates(raw)
        tags_raw, title_txt = extract_tags(rest)
        title_txt = title_txt.strip(" -") or "(sin título)"

        # tags: normaliza y filtra si allowed_tags
        tags_norm_all = sorted({norm_tag(x) for x in tags_raw})
        if allowed_tags is not None:
            tags_norm = [t for t in tags_norm_all if t in allowed_tags]
            tags_display = [t for t in tags_raw if norm_tag(t) in allowed_tags]
        else:
            tags_norm = tags_norm_all
            tags_display = tags_raw

        for tg in tags_norm:
            all_tags_norm.add(tg)

        # fechas/status
        date_items = []
        statuses_set = set()
        dates_iso = []

        for ds in dates:
            d = parse_date(ds)
            if d:
                st = date_status(d, today)
                statuses_set.add(st)
                dates_iso.append(ds)
                date_items.append((ds, st))
            else:
                date_items.append((ds, None))

        current["cards"].append(
            {
                "done": done,
                "title": title_txt,
                "target": target,              # para resolver href luego
                "href": None,                  # se rellena en hook.py
                "date_items": date_items,
                "tags": tags_display,          # ya filtradas si allowed_tags
                "tags_norm": tags_norm,         # para filtros UI
                "dates_iso": dates_iso,
                "statuses": sorted(statuses_set),
                "has_dates": bool(dates_iso),
            }
        )

    return columns, all_tags_norm
