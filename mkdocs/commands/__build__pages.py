from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Sequence

import jinja2

from mkdocs import utils
from mkdocs.exceptions import BuildError
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from ._build_context import get_context

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


log = logging.getLogger(__name__)


def _populate_page(page: Page, config: MkDocsConfig, files: Files, dirty: bool = False) -> None:
    """Read page content from docs_dir and render Markdown."""
    config._current_page = page
    try:
        # When --dirty is used, only read the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        # Run the `pre_page` plugin event
        page = config.plugins.on_pre_page(page, config=config, files=files)

        page.read_source(config)
        assert page.markdown is not None

        # Run `page_markdown` plugin events.
        page.markdown = config.plugins.on_page_markdown(
            page.markdown, page=page, config=config, files=files
        )

        page.render(config, files)
        assert page.content is not None

        # Run `page_content` plugin events.
        page.content = config.plugins.on_page_content(
            page.content, page=page, config=config, files=files
        )
    except Exception as e:
        message = f"Error reading page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise
    finally:
        config._current_page = None


def _build_page(
    page: Page,
    config: MkDocsConfig,
    doc_files: Sequence[File],
    nav: Navigation,
    env: jinja2.Environment,
    dirty: bool = False,
    excluded: bool = False,
) -> None:
    """Pass a Page to theme template and write output to site_dir."""
    config._current_page = page
    try:
        # When --dirty is used, only build the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        log.debug(f"Building page {page.file.src_uri}")

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        context = get_context(nav, doc_files, config, page)

        # Allow 'template:' override in md source files.
        template = env.get_template(page.meta.get('template', 'main.html'))

        # Run `page_context` plugin events.
        context = config.plugins.on_page_context(context, page=page, config=config, nav=nav)

        if excluded:
            page.content = (
                '<div class="mkdocs-draft-marker" title="This page will not be included into the built site.">'
                'DRAFT'
                '</div>' + (page.content or '')
            )

        # Render the template.
        output = template.render(context)

        # Run `post_page` plugin events.
        output = config.plugins.on_post_page(output, page=page, config=config)

        # Write the output file.
        if output.strip():
            utils.write_file(
                output.encode('utf-8', errors='xmlcharrefreplace'), page.file.abs_dest_path
            )
        else:
            log.info(f"Page skipped: '{page.file.src_uri}'. Generated empty output.")

    except Exception as e:
        message = f"Error building page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise
    finally:
        # Deactivate page
        page.active = False
        config._current_page = None
