from __future__ import annotations

import sys
from pathlib import Path
from html import escape

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from tag_colors import load_tag_colors, tag_style, norm_tag  # noqa: E402
from styles import KB_STYLE  # noqa: E402
from script import KB_SCRIPT  # noqa: E402
import parse as kb_parse  # noqa: E402
import links as kb_links  # noqa: E402


DEFAULT_DOC_ROOTS = [
    "research/Developments",
    "Developments",
    "research",
]

ARCHIVE_DOC_ROOTS = [
    "research/Archived",
    "Archived",
    "research/archived",
]

ARCHIVE_COL_KEYWORD = "archiv"

# Solo para separar visualmente en 2 bloques
USER_TAG_SET = {"DDOBRE", "IBOUABDI", "PMASIA", "IBOUADI"}


def on_page_markdown(markdown, page, config, files, **kwargs):
    meta = getattr(page, "meta", {}) or {}
    if not kb_parse.is_obsidian_kanban_board(markdown, meta):
        return markdown

    tag_colors = load_tag_colors()
    today = kb_parse.today_madrid()

    columns, all_tags_norm = kb_parse.parse_board(
        markdown,
        meta,
        today,
        allowed_tags=None,
        archive_keyword=ARCHIVE_COL_KEYWORD,
    )
    if not columns:
        return markdown

    # Resolver href por roots
    for col in columns:
        roots = ARCHIVE_DOC_ROOTS if col.get("archived") else DEFAULT_DOC_ROOTS
        for c in col["cards"]:
            if c.get("target"):
                c["href"] = kb_links.resolve_wikilink_href(c["target"], page, files, config, roots)

    # Sacar completadas a columna extra
    done_cards = []
    for col in columns:
        keep = []
        for c in col["cards"]:
            if c.get("done"):
                done_cards.append(c)
            else:
                keep.append(c)
        col["cards"] = keep

    # filtros: separar users vs normales (colores salen del mismo json)
    all_users_norm = sorted([t for t in all_tags_norm if t in USER_TAG_SET])
    all_tags_norm_only = sorted([t for t in all_tags_norm if t not in USER_TAG_SET])

    def cfg_for(tg_norm: str) -> tuple[str, str]:
        cfg = tag_colors.get(tg_norm, tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
        return cfg.get("bg", "#8080801a"), cfg.get("fg", "#cfcfcf")

    user_chip_html = []
    for tg in all_users_norm:
        bg, fg = cfg_for(tg)
        user_chip_html.append(
            f'<button type="button" class="kb-tagfilter kb-userfilter" data-kb-user="{escape(tg, quote=True)}" '
            f'style="--tg-bg:{escape(bg, quote=True)};--tg-fg:{escape(fg, quote=True)};">'
            f'@{escape(tg)}</button>'
        )

    tag_chip_html = []
    for tg in all_tags_norm_only:
        bg, fg = cfg_for(tg)
        tag_chip_html.append(
            f'<button type="button" class="kb-tagfilter" data-kb-tag="{escape(tg, quote=True)}" '
            f'style="--tg-bg:{escape(bg, quote=True)};--tg-fg:{escape(fg, quote=True)};">'
            f'#{escape(tg)}</button>'
        )

    out = []
    out.append(KB_STYLE)
    out.append('<div class="kb-wrap" data-kb-wrap="1">')

    # Toolbar
    out.append('<div class="kb-toolbar">')

    out.append(
        '<div class="kb-field">'
        '<label>Nombre</label>'
        '<input class="kb-input" type="search" placeholder="Buscar..." data-kb-filter="q" />'
        '</div>'
    )

    out.append(
        '<div class="kb-field">'
        '<label>Fecha</label>'
        '<select class="kb-select" data-kb-filter="status">'
        "<option value=''>Estado: Todas</option>"
        "<option value='past'>Vencidas</option>"
        "<option value='soon'>Próx. 7 días</option>"
        "<option value='later'>Más tarde</option>"
        "<option value='nodate'>Sin fechas</option>"
        "</select>"
        '</div>'
    )

    out.append(
        '<div class="kb-field">'
        '<label>Desde</label>'
        '<input class="kb-input" type="date" data-kb-filter="from" />'
        '</div>'
    )

    out.append(
        '<div class="kb-field">'
        '<label>Hasta</label>'
        '<input class="kb-input" type="date" data-kb-filter="to" />'
        '</div>'
    )

    out.append(
        '<label class="kb-check" title="Mostrar/ocultar columnas archivadas">'
        '<input type="checkbox" data-kb-toggle="archived" />'
        '<span>Ver archivados</span>'
        '</label>'
    )

    out.append(
        '<label class="kb-check" title="Mostrar solo columnas archivadas">'
        '<input type="checkbox" data-kb-toggle="onlyarchived" />'
        '<span>Solo archivados</span>'
        '</label>'
    )

    out.append(
        '<label class="kb-check" title="Mostrar columna de completadas">'
        '<input type="checkbox" data-kb-toggle="donecol" autocomplete="off" />'
        '<span>Ver completadas</span>'
        '</label>'
    )

    out.append('</div>')  # toolbar

    # 2 bloques
    if user_chip_html:
        out.append('<div class="kb-tagbar kb-tagbar-users">' + "".join(user_chip_html) + '</div>')
    if tag_chip_html:
        out.append('<div class="kb-tagbar kb-tagbar-tags">' + "".join(tag_chip_html) + '</div>')

    # ✅ IMPORTANTE: vuelve kb-bleed-right
    out.append('<div class="kb-board kb-bleed-right" data-kb-board="1">')

    def render_card(c: dict, done_visual: bool = False) -> str:
        done_cls = " kb-done" if done_visual else ""
        data_title = escape(c["title"], quote=True)

        tags_user_norm = [t for t in c["tags_norm"] if t in USER_TAG_SET]
        tags_norm_only = [t for t in c["tags_norm"] if t not in USER_TAG_SET]

        data_tags = escape(",".join(tags_norm_only), quote=True)
        data_users = escape(",".join(tags_user_norm), quote=True)
        data_dates = escape(",".join(c["dates_iso"]), quote=True)
        data_statuses = escape(",".join(c["statuses"]), quote=True)
        data_hasdates = "1" if c["has_dates"] else "0"

        attrs = (
            f' data-title="{data_title}"'
            f' data-tags="{data_tags}"'
            f' data-users="{data_users}"'
            f' data-dates="{data_dates}"'
            f' data-statuses="{data_statuses}"'
            f' data-hasdates="{data_hasdates}"'
        )

        parts = []
        if c.get("href"):
            parts.append(f'<a class="kb-card{done_cls}" href="{escape(c["href"], quote=True)}"{attrs}>')
        else:
            parts.append(f'<article class="kb-card{done_cls}"{attrs}>')

        parts.append(f'<div class="kb-card-title">{escape(c["title"])}</div>')

        chips = []
        for ds, st in c["date_items"]:
            cls = f"kb-chip kb-date {st}" if st else "kb-chip kb-date"
            chips.append(f'<span class="{cls}">{escape(ds)}</span>')

        for tag in c["tags"]:
            tnorm = norm_tag(tag)
            style = tag_style(tag_colors, tag)

            if tnorm in USER_TAG_SET:
                chips.append(f'<span class="kb-chip kb-tag kb-user" style="{style}">@{escape(tag)}</span>')
            else:
                chips.append(f'<span class="kb-chip kb-tag" style="{style}">#{escape(tag)}</span>')

        if chips:
            parts.append('<div class="kb-meta">' + "".join(chips) + '</div>')

        parts.append("</a>" if c.get("href") else "</article>")
        return "".join(parts)

    # columnas normales
    for col in columns:
        arch_cls = " kb-archived" if col.get("archived") else ""
        out.append(f'<section class="kb-col{arch_cls}">')
        out.append(f'<header class="kb-col-title">{escape(col["title"])}</header>')
        out.append('<div class="kb-cards">')

        if not col["cards"]:
            out.append('<div class="kb-empty">—</div>')
        else:
            for c in col["cards"]:
                out.append(render_card(c, done_visual=False))
            out.append('<div class="kb-empty" data-kb-empty="filtered" style="display:none;">Sin resultados</div>')

        out.append('</div></section>')

    # columna completadas (oculta por CSS hasta toggle)
    out.append('<section class="kb-col kb-done-col">')
    out.append('<header class="kb-col-title">Completadas</header>')
    out.append('<div class="kb-cards">')

    if not done_cards:
        out.append('<div class="kb-empty">—</div>')
    else:
        for c in done_cards:
            out.append(render_card(c, done_visual=True))
        out.append('<div class="kb-empty" data-kb-empty="filtered" style="display:none;">Sin resultados</div>')

    out.append('</div></section>')

    out.append('</div>')      # board
    out.append(KB_SCRIPT)     # JS
    out.append('</div>')      # wrap

    return "\n".join(out)
