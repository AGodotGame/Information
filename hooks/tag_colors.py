from __future__ import annotations

import json
from pathlib import Path

_TAG_COLORS = None

_USER_TAG_COLORS = None

def load_user_tag_colors() -> dict:
    """Carga hooks/obsidian_kanban/user_tag_colors.json y normaliza keys a MAYÚSCULAS."""
    global _USER_TAG_COLORS
    if _USER_TAG_COLORS is not None:
        return _USER_TAG_COLORS

    here = Path(__file__).resolve().parent
    cfg_path = here / "user_tag_colors.json"

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
        key = "__default__" if k == "__default__" else norm_tag(k)
        normalized[key] = v

    normalized.setdefault("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"})
    _USER_TAG_COLORS = normalized
    return normalized

def norm_tag(tag: str) -> str:
    return tag.strip().lstrip("#").upper()


def load_tag_colors() -> dict:
    """Carga hooks/obsidian_kanban/tag_colors.json y normaliza keys a MAYÚSCULAS."""
    global _TAG_COLORS
    if _TAG_COLORS is not None:
        return _TAG_COLORS

    here = Path(__file__).resolve().parent
    cfg_path = here / "tag_colors.json"

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
        key = "__default__" if k == "__default__" else norm_tag(k)
        normalized[key] = v

    normalized.setdefault("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"})
    _TAG_COLORS = normalized
    return normalized


def tag_style(tag_colors: dict, tag: str) -> str:
    cfg = tag_colors.get(norm_tag(tag), tag_colors.get("__default__", {"bg": "#8080801a", "fg": "#cfcfcf"}))
    bg = cfg.get("bg", "#8080801a")
    fg = cfg.get("fg", "#cfcfcf")
    return f"background-color: {bg}; color: {fg}; border-color: {fg};"
