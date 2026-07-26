"""
SciOS-NG Runtime Observability Dashboard

viewer.py

Part 1. Identity Layer
"""

from __future__ import annotations

import copy
import uuid
import time
from typing import Any


class DashboardViewer:
    """
    Dashboard Viewer Runtime Component.

    Responsible for presenting observability
    data from SciOS-NG runtime.
    """


    # ======================================================
    # Part 1. Identity
    # ======================================================

    def __init__(
        self,
        name: str = "SciOS Dashboard Viewer",
        version: str = "0.1.0",
        description: str | None = None,
        viewer_type: str = "dashboard",
    ):
        """
        Initialize Viewer identity.
        """


        # --------------------------------------------------
        # Unique Identity
        # --------------------------------------------------

        self.id: str = str(
            uuid.uuid4()
        )


        self.component_id: str = (
            f"viewer-{self.id}"
        )


        # --------------------------------------------------
        # Metadata Identity
        # --------------------------------------------------

        self.name: str = name


        self.version: str = version


        self.description: str = (
            description
            or
            "SciOS-NG Observability Dashboard Viewer"
        )


        self.viewer_type: str = (
            viewer_type
        )


        # --------------------------------------------------
        # Runtime timestamps
        # --------------------------------------------------

        self.created_at: float = (
            time.time()
        )


        self.updated_at: float = (
            self.created_at
        )


    # ======================================================
    # Identity Properties
    # ======================================================

    @property
    def identity(
        self,
    ) -> dict[str, Any]:
        """
        Return identity information.
        """

        return {

            "id":
                self.id,

            "component_id":
                self.component_id,

            "name":
                self.name,

            "version":
                self.version,

            "description":
                self.description,

            "viewer_type":
                self.viewer_type,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,
        }


    # ======================================================
    # Identity Update
    # ======================================================

    def update_identity(
        self,
        *,
        name: str | None = None,
        version: str | None = None,
        description: str | None = None,
        viewer_type: str | None = None,
    ) -> None:
        """
        Update viewer identity metadata.
        """


        if name is not None:

            self.name = name


        if version is not None:

            self.version = version


        if description is not None:

            self.description = description


        if viewer_type is not None:

            self.viewer_type = viewer_type


        self.updated_at = time.time()


    # ======================================================
    # Identity Validation
    # ======================================================

    def validate_identity(
        self,
    ) -> bool:
        """
        Validate identity fields.
        """

        if not self.id:

            return False


        if not self.name:

            return False


        if not self.version:

            return False


        if not self.viewer_type:

            return False


        return True


    # ======================================================
    # Python Protocol
    # ======================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"type={self.viewer_type!r}"
            f")"
        )


    def __str__(
        self,
    ) -> str:
        """
        Human readable identity.
        """

        return (
            f"{self.name} "
            f"v{self.version} "
            f"({self.viewer_type})"
        )
# ======================================================
# Part 2. Configuration
# ======================================================


# ------------------------------------------------------
# Generic Options
# ------------------------------------------------------

self.options: dict[str, Any] = {}


# ------------------------------------------------------
# UI Theme
# ------------------------------------------------------

self.theme: str = (
    "default"
)


# ------------------------------------------------------
# Layout Mode
# ------------------------------------------------------

self.layout: str = (
    "auto"
)


# ------------------------------------------------------
# Refresh Configuration
# ------------------------------------------------------

self.refresh_interval: float = (
    5.0
)


self.auto_refresh: bool = (
    True
)


# ------------------------------------------------------
# Data Limit
# ------------------------------------------------------

self.max_items: int = (
    100
)


# ------------------------------------------------------
# Rendering Backend
# ------------------------------------------------------

self.renderer: str = (
    "dict"
)
# ======================================================
# Part 3. Runtime State
# ======================================================


# ------------------------------------------------------
# Lifecycle Flags
# ------------------------------------------------------

self._enabled: bool = True


self._frozen: bool = False


self._closed: bool = False



# ------------------------------------------------------
# Runtime State
# ------------------------------------------------------

self.state: str = (
    "ready"
)


self.running: bool = (
    False
)


self.dirty: bool = (
    False
)



# ------------------------------------------------------
# View Registry
# ------------------------------------------------------

self.views: dict[str, Any] = {}



# ------------------------------------------------------
# Data Sources
# ------------------------------------------------------

self.data_sources: dict[str, Any] = {}



# ------------------------------------------------------
# Runtime Counters
# ------------------------------------------------------

self.render_count: int = 0


self.refresh_count: int = 0


self.last_render_at: float | None = None


self.last_refresh_at: float | None = None
# ======================================================
# Part 4. Data Binding
# ======================================================

self.bindings: dict[str, Any] = {}


self.source_metadata: dict[str, dict] = {}


self.sync_status: dict[str, Any] = {}
# ======================================================
# Part 5. View API
# ======================================================

self.active_view: str | None = None


self.view_history: list[str] = []


self.view_counter: int = 0
# ======================================================
# Part 6. Rendering
# ======================================================

self.renderers = {

    "dict":
        self.render_dict,

    "json":
        self.render_json,

    "html":
        self.render_html,

    "table":
        self.render_table,

}


self.last_render = None


self.render_count = 0
# ======================================================
# Part 7. Dashboard Widgets
# ======================================================

self.widgets: dict[str, dict] = {}


self.widget_counter: int = 0


self.widget_history: list[str] = []
# ======================================================
# Part 8. Events & Hooks
# ======================================================

self.events: list[dict] = []


self.max_events: int = 1000


self.handlers: dict[str, list] = {

    "before_render": [],

    "after_render": [],

    "before_refresh": [],

    "after_refresh": [],

    "before_update": [],

    "after_update": [],

}
# ======================================================
# Part 9. Lifecycle Management
# ======================================================

self.lifecycle: str = (
    "created"
)


self.started_at: float | None = None


self.stopped_at: float | None = None


self.shutdown_reason: str | None = None
# ======================================================
# Part 10. Python Protocols
# ======================================================

import copy


# ------------------------------------------------------
# __repr__()
# ------------------------------------------------------

def __repr__(
    self,
) -> str:
    """
    Developer representation.

    Example:
        DashboardViewer(
            id='xxx',
            name='SciOS Dashboard Viewer',
            state='running'
        )
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self.id!r}, "
        f"name={self.name!r}, "
        f"version={self.version!r}, "
        f"type={self.viewer_type!r}, "
        f"state={self.state!r}, "
        f"views={len(self.views)}, "
        f"widgets={len(self.widgets)}"
        f")"
    )


# ------------------------------------------------------
# __str__()
# ------------------------------------------------------

def __str__(
    self,
) -> str:
    """
    Human readable representation.
    """

    return (
        f"{self.name} "
        f"v{self.version} "
        f"[{self.state}] "
        f"views={len(self.views)} "
        f"widgets={len(self.widgets)}"
    )


# ------------------------------------------------------
# __len__()
# ------------------------------------------------------

def __len__(
    self,
) -> int:
    """
    Number of registered views.

    Example:
        len(viewer)
    """

    return len(
        self.views
    )


# ------------------------------------------------------
# __iter__()
# ------------------------------------------------------

def __iter__(
    self,
):
    """
    Iterate through dashboard views.

    Example:

        for view in viewer:
            ...
    """

    return iter(
        self.views.values()
    )


# ------------------------------------------------------
# __contains__()
# ------------------------------------------------------

def __contains__(
    self,
    item,
) -> bool:
    """
    Check whether view/widget exists.

    Example:

        "metrics" in viewer
    """


    if item in self.views:

        return True


    if item in self.widgets:

        return True


    return False


# ------------------------------------------------------
# __getitem__()
# ------------------------------------------------------

def __getitem__(
    self,
    key,
):
    """
    Access views/widgets.

    Example:

        viewer["metrics"]

    """


    if key in self.views:

        return self.views[key]


    if key in self.widgets:

        return self.widgets[key]


    raise KeyError(
        f"Unknown dashboard item: {key}"
    )


# ------------------------------------------------------
# __call__()
# ------------------------------------------------------

def __call__(
    self,
    view=None,
    *,
    mode=None,
):
    """
    Make DashboardViewer callable.

    Example:

        viewer()

        viewer(
            "metrics",
            mode="json"
        )
    """


    return self.render(
        view,
        mode=mode
    )


# ------------------------------------------------------
# __copy__()
# ------------------------------------------------------

def __copy__(
    self,
):
    """
    Shallow copy.

    Keeps references to:
        - data sources
        - engines
        - handlers

    """

    cls = self.__class__


    new = cls.__new__(
        cls
    )


    new.__dict__.update(
        self.__dict__
    )


    return new


# ------------------------------------------------------
# __deepcopy__()
# ------------------------------------------------------

def __deepcopy__(
    self,
    memo,
):
    """
    Deep copy.

    Clone complete runtime state.
    """


    cls = self.__class__


    new = cls.__new__(
        cls
    )


    memo[id(self)] = new


    for key, value in self.__dict__.items():

        setattr(
            new,
            key,
            copy.deepcopy(
                value,
                memo
            )
        )


    return new