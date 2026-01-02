from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import jinja2  # noqa: F401 (se mantiene por coherencia con el original)

from mkdocs import utils
from mkdocs.exceptions import Abort, BuildError
from mkdocs.structure.files import InclusionLevel, get_files, set_exclusions
from mkdocs.structure.nav import get_navigation
from mkdocs.structure.pages import Page
from mkdocs.utils import DuplicateFilter  # noqa: F401 - legacy re-export
from mkdocs.utils import templates  # noqa: F401 - legacy re-export

from ._build_pages import _build_page, _populate_page
from ._build_templates import _build_extra_template, _build_theme_template

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


log = logging.getLogger(__name__)


def build(config: MkDocsConfig, *, serve_url: str | None = None, dirty: bool = False) -> None:
    """Perform a full site build."""
    logger = logging.getLogger('mkdocs')

    # Add CountHandler for strict mode
    warning_counter = utils.CountHandler()
    warning_counter.setLevel(logging.WARNING)
    if config.strict:
        logging.getLogger('mkdocs').addHandler(warning_counter)

    inclusion = InclusionLevel.is_in_serve if serve_url else InclusionLevel.is_included

    try:
        start = time.monotonic()

        # Run `config` plugin events.
        config = config.plugins.on_config(config)

        # Run `pre_build` plugin events.
        config.plugins.on_pre_build(config=config)

        if not dirty:
            log.info("Cleaning site directory")
            utils.clean_directory(config.site_dir)
        else:  # pragma: no cover
            # Warn user about problems that may occur with --dirty option
            log.warning(
                "A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                " links within your site. This option is designed for site development purposes only."
            )

        if not serve_url:  # pragma: no cover
            log.info(f"Building documentation to directory: {config.site_dir}")
            if dirty and site_directory_contains_stale_files(config.site_dir):
                log.info("The directory contains stale files. Use --clean to remove them.")

        # First gather all data from all files/pages to ensure all data is consistent across all pages.

        files = get_files(config)
        env = config.theme.get_env()
        files.add_files_from_theme(env, config)

        # Run `files` plugin events.
        files = config.plugins.on_files(files, config=config)
        # If plugins have added files but haven't set their inclusion level, calculate it again.
        set_exclusions(files, config)

        nav = get_navigation(files, config)

        # Run `nav` plugin events.
        nav = config.plugins.on_nav(nav, config=config, files=files)

        log.debug("Reading markdown pages.")
        excluded = []
        for file in files.documentation_pages(inclusion=inclusion):
            log.debug(f"Reading: {file.src_uri}")
            if file.page is None and file.inclusion.is_not_in_nav():
                if serve_url and file.inclusion.is_excluded():
                    excluded.append(urljoin(serve_url, file.url))
                Page(None, file, config)
            assert file.page is not None
            _populate_page(file.page, config, files, dirty)
        if excluded:
            log.info(
                "The following pages are being built only for the preview "
                "but will be excluded from `mkdocs build` per `draft_docs` config:\n  - "
                + "\n  - ".join(excluded)
            )

        # Run `env` plugin events.
        env = config.plugins.on_env(env, config=config, files=files)

        # Start writing files to site_dir now that all data is gathered. Note that order matters. Files
        # with lower precedence get written first so that files with higher precedence can overwrite them.

        log.debug("Copying static assets.")
        files.copy_static_files(dirty=dirty, inclusion=inclusion)

        for template in config.theme.static_templates:
            _build_theme_template(template, env, files, config, nav)

        for template in config.extra_templates:
            _build_extra_template(template, files, config, nav)

        log.debug("Building markdown pages.")
        doc_files = files.documentation_pages(inclusion=inclusion)
        for file in doc_files:
            assert file.page is not None
            _build_page(
                file.page, config, doc_files, nav, env, dirty, excluded=file.inclusion.is_excluded()
            )

        log_level = config.validation.links.anchors
        for file in doc_files:
            assert file.page is not None
            file.page.validate_anchor_links(files=files, log_level=log_level)

        # Run `post_build` plugin events.
        config.plugins.on_post_build(config=config)

        if counts := warning_counter.get_counts():
            msg = ', '.join(f'{v} {k.lower()}s' for k, v in counts)
            raise Abort(f'Aborted with {msg} in strict mode!')

        log.info(f'Documentation built in {time.monotonic() - start:.2f} seconds')

    except Exception as e:
        # Run `build_error` plugin events.
        config.plugins.on_build_error(error=e)
        if isinstance(e, BuildError):
            log.error(str(e))
            raise Abort('Aborted with a BuildError!')
        raise

    finally:
        logger.removeHandler(warning_counter)


def site_directory_contains_stale_files(site_directory: str) -> bool:
    """Check if the site directory contains stale files from a previous build."""
    return bool(os.path.exists(site_directory) and os.listdir(site_directory))
