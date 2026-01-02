from __future__ import annotations

import gzip
import logging
import os
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import jinja2
from jinja2.exceptions import TemplateNotFound

from mkdocs import utils
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation

from ._build_context import get_context

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


log = logging.getLogger(__name__)


def _build_template(
    name: str, template: jinja2.Template, files: Files, config: MkDocsConfig, nav: Navigation
) -> str:
    """Return rendered output for given template as a string."""
    # Run `pre_template` plugin events.
    template = config.plugins.on_pre_template(template, template_name=name, config=config)

    if utils.is_error_template(name):
        # Force absolute URLs in the nav of error pages and account for the
        # possibility that the docs root might be different than the server root.
        # See https://github.com/mkdocs/mkdocs/issues/77.
        # However, if site_url is not set, assume the docs root and server root
        # are the same. See https://github.com/mkdocs/mkdocs/issues/1598.
        base_url = urlsplit(config.site_url or '/').path
    else:
        base_url = utils.get_relative_url('.', name)

    context = get_context(nav, files, config, base_url=base_url)

    # Run `template_context` plugin events.
    context = config.plugins.on_template_context(context, template_name=name, config=config)

    output = template.render(context)

    # Run `post_template` plugin events.
    output = config.plugins.on_post_template(output, template_name=name, config=config)

    return output


def _build_theme_template(
    template_name: str, env: jinja2.Environment, files: Files, config: MkDocsConfig, nav: Navigation
) -> None:
    """Build a template using the theme environment."""
    log.debug(f"Building theme template: {template_name}")

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        log.warning(f"Template skipped: '{template_name}' not found in theme directories.")
        return

    output = _build_template(template_name, template, files, config, nav)

    if output.strip():
        output_path = os.path.join(config.site_dir, template_name)
        utils.write_file(output.encode('utf-8'), output_path)

        if template_name == 'sitemap.xml':
            log.debug(f"Gzipping template: {template_name}")
            gz_filename = f'{output_path}.gz'
            with open(gz_filename, 'wb') as f:
                timestamp = utils.get_build_timestamp(
                    pages=[f.page for f in files.documentation_pages() if f.page is not None]
                )
                with gzip.GzipFile(
                    fileobj=f, filename=gz_filename, mode='wb', mtime=timestamp
                ) as gz_buf:
                    gz_buf.write(output.encode('utf-8'))
    else:
        log.info(f"Template skipped: '{template_name}' generated empty output.")


def _build_extra_template(template_name: str, files: Files, config: MkDocsConfig, nav: Navigation):
    """Build user templates which are not part of the theme."""
    log.debug(f"Building extra template: {template_name}")

    file = files.get_file_from_path(template_name)
    if file is None:
        log.warning(f"Template skipped: '{template_name}' not found in docs_dir.")
        return

    try:
        template = jinja2.Template(file.content_string)
    except Exception as e:
        log.warning(f"Error reading template '{template_name}': {e}")
        return

    output = _build_template(template_name, template, files, config, nav)

    if output.strip():
        utils.write_file(output.encode('utf-8'), file.abs_dest_path)
    else:
        log.info(f"Template skipped: '{template_name}' generated empty output.")
