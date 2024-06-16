import os
from pathlib import Path
from typing import *  # type: ignore

import rio.components.class_container
import rio.components.dev_tools_connector

from . import (
    deploy_page,
    docs_page,
    icons_page,
    project_page,
    rio_developer_page,
    theme_picker_page,
    tree_page,
)


class DevToolsSidebar(rio.Component):
    show_rio_developer_page: bool = False

    selected_page: (
        Literal[
            "project",
            "tree",
            "docs",
            "deploy",
            "rio-developer",
        ]
        | None
    ) = None

    def __post_init__(self) -> None:
        # Decide whether to show the Rio Developer page. Ideally, the page would
        # be displayed to developers of Rio itself - without them having to do
        # anything - while not showing it to developers _using_ Rio.
        #
        # One easy way to achieve this is to look whether a `pyproject.toml`
        # file is located right outside of Rio's root directory.
        rio_root_directory = Path(rio.__file__).parent
        pyproject_toml_path = rio_root_directory.parent / "pyproject.toml"
        self.show_rio_developer_page = pyproject_toml_path.exists()

        # HOWEVER, always allow forcing the tools to be visible via an
        # environment variable:
        try:
            os.environ["RIO_DEV"]
        except KeyError:
            pass
        else:
            self.show_rio_developer_page = True

    def get_selected_page(self) -> rio.Component | None:
        REGULAR_PAGE_WIDTH = 22
        WIDE_PAGE_WIDTH = 32

        # Nothing selected
        if self.selected_page is None:
            return None

        # Project
        if self.selected_page == "project":
            return project_page.ProjectPage(
                width=REGULAR_PAGE_WIDTH,
            )

        # Tree
        if self.selected_page == "tree":
            return tree_page.TreePage(
                width=WIDE_PAGE_WIDTH,
            )

        # Icons
        if self.selected_page == "icons":
            return icons_page.IconsPage(
                width=WIDE_PAGE_WIDTH,
            )

        # Theme
        if self.selected_page == "theme":
            return theme_picker_page.ThemePickerPage(
                width=WIDE_PAGE_WIDTH,
            )

        # Docs
        if self.selected_page == "docs":
            return docs_page.DocsPage(
                width=REGULAR_PAGE_WIDTH,
            )

        # Deploy
        if self.selected_page == "deploy":
            return deploy_page.DeployPage(
                width=REGULAR_PAGE_WIDTH,
            )

        # Rio Developer
        if self.selected_page == "rio-developer":
            return rio_developer_page.RioDeveloperPage(
                width=REGULAR_PAGE_WIDTH,
            )

        # Anything else / TODO
        return rio.Text(
            f"TODO: {self.selected_page}",
            justify="center",
            margin=2,
            width=REGULAR_PAGE_WIDTH,
        )

    def build(self) -> rio.Component:
        names = [
            # "Project",
            "Tree",
            "Icons",
            "Theme",
            # "Docs",
            "Deploy",
        ]

        icons = [
            # "rio/logo",
            "material/view-quilt",
            "material/emoji-people",
            "material/palette",
            # "material/library-books",
            "material/rocket-launch",
        ]

        values = [
            # "project",
            "tree",
            "icons",
            "theme",
            # "docs",
            "deploy",
        ]

        # If developing Rio itself, show the Rio Developer page
        if self.show_rio_developer_page:
            names.append("Rio Dev")
            icons.append("rio/logo")
            values.append("rio-developer")

        return rio.Rectangle(
            # Make sure everything has a background, otherwise the component
            # highlighter will be visible behind this component
            fill=self.session.theme.background_color,
            content=rio.Row(
                # Big fat line to separate the dev tools from the rest of the page
                rio.Rectangle(
                    width=0.3,
                    fill=self.session.theme.primary_palette.background,
                ),
                # Currently active page
                rio.components.class_container.ClassContainer(
                    rio.Switcher(self.get_selected_page()),
                    classes=[
                        "rio-switcheroo-neutral",
                        "rio-dev-tools-background",
                    ],
                ),
                # Navigation
                rio.Column(
                    rio.SwitcherBar(
                        names=names,
                        icons=icons,
                        values=values,
                        allow_none=True,
                        orientation="vertical",
                        spacing=2,
                        color="primary",
                        selected_value=self.bind().selected_page,
                        margin=0.2,
                    ),
                    rio.Spacer(),
                    rio.components.dev_tools_connector.DevToolsConnector(),
                ),
            ),
        )
