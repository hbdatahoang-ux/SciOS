"""
SciOS Cognitive Plugin Manager
==============================

Plugin registry and lifecycle manager for CognitiveCore.

Responsibilities
-----------------
- Register cognitive plugins
- Retrieve plugins
- Execute plugins
- Remove plugins
- Inspect runtime state
- Provide deterministic plugin lifecycle

Python 3.11+
"""

from __future__ import annotations

from typing import (
    Any,
    Iterator,
    Mapping,
)


__all__ = [
    "PluginManager",
]



class PluginManager:
    """
    Central plugin registry for CognitiveCore.

    Example
    -------

    manager = PluginManager()

    manager.register(
        "memory",
        MemoryPlugin()
    )

    manager.execute(
        "memory",
        query="hello"
    )

    """



    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
    ) -> None:

        self._plugins: dict[str, Any] = {}



    # ======================================================
    # Registration
    # ======================================================

    def register(
        self,
        name: str,
        plugin: Any,
    ) -> None:
        """
        Register a plugin.

        Parameters
        ----------
        name:
            Unique plugin identifier.

        plugin:
            Plugin instance or callable.

        """

        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "Plugin name must be str"
            )


        if not name:

            raise ValueError(
                "Plugin name cannot be empty"
            )


        self._plugins[name] = plugin



    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove plugin.

        Raises
        ------
        KeyError
            If plugin does not exist.
        """

        if name not in self._plugins:

            raise KeyError(
                f"Plugin not found: {name}"
            )


        del self._plugins[name]



    def clear(
        self,
    ) -> None:
        """
        Remove all plugins.
        """

        self._plugins.clear()



    # ======================================================
    # Query
    # ======================================================

    def list_plugins(
        self,
    ) -> list[str]:
        """
        Return registered plugin names.
        """

        return list(
            self._plugins.keys()
        )



    def get(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve plugin.

        Raises
        ------
        KeyError
            Plugin does not exist.
        """

        if name not in self._plugins:

            raise KeyError(
                f"Plugin not found: {name}"
            )


        return self._plugins[name]



    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check plugin existence.
        """

        return name in self._plugins



    # ======================================================
    # Execution
    # ======================================================

    def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute plugin.

        Supported plugin styles:

        1. Object plugin

            plugin.run(**kwargs)

        2. Callable plugin

            plugin(**kwargs)

        """

        plugin = self.get(
            name
        )


        if hasattr(
            plugin,
            "run",
        ):

            return plugin.run(
                **kwargs
            )


        if callable(
            plugin,
        ):

            return plugin(
                **kwargs
            )


        return plugin



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize all plugins.

        Calls:

            plugin.initialize()

        if available.
        """

        for plugin in self._plugins.values():

            method = getattr(
                plugin,
                "initialize",
                None,
            )

            if callable(method):

                method()



    def shutdown(
        self,
    ) -> None:
        """
        Shutdown all plugins.

        Calls:

            plugin.shutdown()

        if available.
        """

        for plugin in self._plugins.values():

            method = getattr(
                plugin,
                "shutdown",
                None,
            )

            if callable(method):

                method()



    # ======================================================
    # Serialization / Diagnostics
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Runtime status.
        """

        return {

            "count":
                len(self._plugins),

            "plugins":
                self.list_plugins(),

        }



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize manager state.
        """

        return self.status()



    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "PluginManager":
        """
        Restore empty manager.

        Plugin objects cannot be restored
        automatically.
        """

        manager = cls()

        return manager



    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._plugins
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._plugins



    def __iter__(
        self,
    ) -> Iterator[str]:

        return iter(
            self._plugins
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "PluginManager("
            f"plugins={len(self._plugins)}"
            ")"
        )