from __future__ import annotations

import sys
from pathlib import Path
from html import escape

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from tag_colors import load_tag_colors, tag_style  # noqa: E402
from styles import KB_STYLE  # noqa: E402
from script import KB_SCRIPT  # noqa: E402
import parse as kb_parse  # noqa: E402
import links as kb_links  # noqa: E402


# ✅ NUEVOS ROOTS (prioridad primero)
# Normal: preferir Developments (si está dentro de research y/o si es carpeta top-level)
DEFAULT_DOC_ROOTS = [
    "research/Developments",
    "Developments",
    "research",
]

# Archivados: preferir Archived (si está dentro de research y/o top-level)
ARCHIVE_DOC_ROOTS = [
    "research/Archived",
    "Archived",
    "research/archived",   # por si alguien lo escribió en minúsculas (opcional)
]

# "archiv" sigue funcionando porque "Archived" contiene "archiv"
ARCHIVE_COL_KEYWORD = "archiv"


def on_page_markdown(markdown, page, config, files, **kwargs):
    meta = getattr(page, "meta", {}) or {}
    if not kb_parse.is_obsidian_kanban_board(markdown, meta):
        return markdown

    tag_colors = load_tag_colors()

    # ✅ Solo permitir tags definidos en tag_colors.json (excepto __default__)
    allowed_tags = {k for k in tag_colors.keys() if k != "__default__"}

    today = kb_parse.today_madrid()

    columns, all_tags_norm = kb_parse.parse_board(
        markdown,
        meta,
        today,
        allowed_tags=allowed_tags,
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

    # ✅ Tag chips (toggle) apagados por defecto; colores solo cuando .is-active
    tag_chip_html = []
    for tg in sorted(all_tags_norm):
        cfg = tag_colors.get(tg, tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
        bg = cfg.get("bg", "#8080801a")
        fg = cfg.get("fg", "#cfcfcf")

        # Guardamos colores como CSS variables (NO se aplican hasta is-active)
        tag_chip_html.append(
            f'<button type="button" class="kb-tagfilter" data-kb-tag="{escape(tg)}" '
            f'style="--tg-bg:{escape(bg)};--tg-fg:{escape(fg)};">'
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
        "</div>"
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

    # ✅ “Ver archivados” (como antes)
    out.append(
        '<label class="kb-check" title="Mostrar/ocultar columnas archivadas">'
        '<input type="checkbox" data-kb-toggle="archived" />'
        '<span>Ver archivados</span>'
        '</label>'
    )

    # ✅ NUEVO: “Solo archivados” (oculta todo menos archivados)
    out.append(
        '<label class="kb-check" title="Mostrar solo columnas archivadas">'
        '<input type="checkbox" data-kb-toggle="onlyarchived" />'
        '<span>Solo archivados</span>'
        '</label>'
    )

    out.append('</div>')  # toolbar

    if tag_chip_html:
        out.append('<div class="kb-tagbar">' + "".join(tag_chip_html) + "</div>")

    # Board
    out.append('<div class="kb-board kb-bleed-right" data-kb-board="1">')

    for col in columns:
        arch_cls = " kb-archived" if col.get("archived") else ""
        out.append(f'<section class="kb-col{arch_cls}">')
        out.append(f'<header class="kb-col-title">{escape(col["title"])}</header>')
        out.append('<div class="kb-cards">')

        if not col["cards"]:
            out.append('<div class="kb-empty">—</div>')
        else:
            for c in col["cards"]:
                done_cls = " kb-done" if c["done"] else ""

                data_title = escape(c["title"], quote=True)
                data_tags = escape(",".join(c["tags_norm"]), quote=True)
                data_dates = escape(",".join(c["dates_iso"]), quote=True)
                data_statuses = escape(",".join(c["statuses"]), quote=True)
                data_hasdates = "1" if c["has_dates"] else "0"

                attrs = (
                    f' data-title="{data_title}"'
                    f' data-tags="{data_tags}"'
                    f' data-dates="{data_dates}"'
                    f' data-statuses="{data_statuses}"'
                    f' data-hasdates="{data_hasdates}"'
                )

                if c.get("href"):
                    out.append(f'<a class="kb-card{done_cls}" href="{escape(c["href"], quote=True)}"{attrs}>')
                else:
                    out.append(f'<article class="kb-card{done_cls}"{attrs}>')

                out.append(f'<div class="kb-card-title">{escape(c["title"])}</div>')

                chips = []

                for ds, st in c["date_items"]:
                    cls = f"kb-chip kb-date {st}" if st else "kb-chip kb-date"
                    chips.append(f'<span class="{cls}">{escape(ds)}</span>')

                # tags en tarjetas (siguen con color siempre, porque informan)
                for tag in c["tags"]:
                    style = tag_style(tag_colors, tag)
                    chips.append(f'<span class="kb-chip kb-tag" style="{style}">#{escape(tag)}</span>')

                if chips:
                    out.append('<div class="kb-meta">' + "".join(chips) + "</div>")

                out.append("</a>" if c.get("href") else "</article>")

            out.append('<div class="kb-empty" data-kb-empty="filtered" style="display:none;">Sin resultados</div>')

        out.append("</div></section>")

    out.append("</div>")      # board
    out.append(KB_SCRIPT)     # JS
    out.append("</div>")      # wrap

    return "\n".join(out)
