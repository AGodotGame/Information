from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import mkdocs
from mkdocs import utils
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.utils import templates

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


def get_context(
    nav: Navigation,
    files: Sequence[File] | Files,
    config: MkDocsConfig,
    page: Page | None = None,
    base_url: str = '',
) -> templates.TemplateContext:
    """Return the template context for a given page or template."""
    if page is not None:
        base_url = utils.get_relative_url('.', page.url)

    extra_javascript = [
        utils.normalize_url(str(script), page, base_url) for script in config.extra_javascript
    ]
    extra_css = [utils.normalize_url(path, page, base_url) for path in config.extra_css]

    if isinstance(files, Files):
        files = files.documentation_pages()

    return templates.TemplateContext(
        nav=nav,
        pages=files,
        base_url=base_url,
        extra_css=extra_css,
        extra_javascript=extra_javascript,
        mkdocs_version=mkdocs.__version__,
        build_date_utc=utils.get_build_datetime(),
        config=config,
        page=page,
    )
