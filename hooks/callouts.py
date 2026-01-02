# hooks/obsidian_callouts.py
from __future__ import annotations
import re

# > [!note] Title
# > content
CALLOUT_START = re.compile(r"^(\s*)>\s*\[!([^\]]+)\]\s*([+-])?\s*(.*)\s*$")
QUOTE_LINE = re.compile(r"^\s*>\s?(.*)$")

KNOWN_TYPES = {
    "note", "abstract", "info", "tip", "success", "question", "warning",
    "failure", "danger", "bug", "example", "quote", "todo"
}

TYPE_MAP = {
    "todo": "info",      # Material no tiene "todo" como tal; lo pintamos como info
    "abstract": "info",
}


def _escape_title(s: str) -> str:
    return s.replace('"', '\\"')


def on_page_markdown(markdown, page, config, files, **kwargs):
    lines = (markdown or "").splitlines()
    out = []
    i = 0

    while i < len(lines):
        m = CALLOUT_START.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        indent, raw_type, fold, rest_title = m.groups()
        raw_type_str = (raw_type or "").strip()
        type_l = raw_type_str.lower()

        # Si lo de dentro no es un tipo conocido, lo tratamos como título (tu caso típico)
        if type_l not in KNOWN_TYPES:
            callout_type = "info"
            title = raw_type_str if not rest_title else f"{raw_type_str} {rest_title}".strip()
        else:
            callout_type = TYPE_MAP.get(type_l, type_l)
            title = rest_title.strip() or raw_type_str

        # plegable: Obsidian usa + / -
        # Material: ???  (cerrado) y ???+ (abierto)
        if fold:
            marker = "???+" if fold == "+" else "???"
        else:
            marker = "!!!"

        out.append(f'{indent}{marker} {callout_type} "{_escape_title(title)}"')

        # consumir el bloque quote completo
        i += 1
        while i < len(lines):
            qm = QUOTE_LINE.match(lines[i])
            if not qm:
                break
            body = qm.group(1)
            out.append(f"{indent}    {body}")
            i += 1

        out.append("")  # separador

    return "\n".join(out)
