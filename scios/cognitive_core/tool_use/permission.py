"""
SciOS Tool Permission Manager
=============================

Permission control layer for Tool Use.

Responsibilities
----------------
- Manage tool permissions.
- Grant/revoke access.
- Validate tool operations.
- Provide diagnostics.
- Maintain backward-compatible API.

Python 3.11+
"""

from __future__ import annotations


from typing import (
    Any,
)


__all__ = [
    "PermissionManager",
]



class PermissionManager:
    """
    Tool permission manager.

    Examples
    --------

    pm = PermissionManager()

    pm.grant(
        "filesystem",
        "read",
    )

    pm.check(
        "filesystem",
        "read",
    )

    pm.check(
        "filesystem",
        {
            "action": "read"
        },
    )
    """



    def __init__(
        self,
    ) -> None:

        self._permissions: dict[
            str,
            set[str],
        ] = {}



    # ======================================================
    # Grant
    # ======================================================

    def grant(
        self,
        tool_name: str,
        permission: str,
    ) -> None:
        """
        Grant permission to tool.
        """

        if not tool_name:
            raise ValueError(
                "tool_name cannot be empty"
            )

        if not permission:
            raise ValueError(
                "permission cannot be empty"
            )


        self._permissions.setdefault(
            tool_name,
            set(),
        ).add(
            permission
        )



    # ======================================================
    # Revoke
    # ======================================================

    def revoke(
        self,
        tool_name: str,
        permission: str,
    ) -> None:
        """
        Remove permission.
        """

        permissions = self._permissions.get(
            tool_name
        )


        if not permissions:
            return


        permissions.discard(
            permission
        )


        if not permissions:

            self._permissions.pop(
                tool_name,
                None,
            )



    # ======================================================
    # Check
    # ======================================================

    def check(
        self,
        tool_name: str,
        request: str | dict[str, Any],
    ) -> bool:
        """
        Check whether operation is allowed.

        Supported:

        check(
            "filesystem",
            "read"
        )


        check(
            "filesystem",
            {
                "action": "read"
            }
        )
        """

        action: str | None = None


        # ----------------------------------------------
        # String API
        # ----------------------------------------------

        if isinstance(
            request,
            str,
        ):

            action = request



        # ----------------------------------------------
        # Dictionary API
        # ----------------------------------------------

        elif isinstance(
            request,
            dict,
        ):

            action = (

                request.get(
                    "action"
                )

                or

                request.get(
                    "operation"
                )

            )


        if not action:

            return False


        return (

            action

            in

            self._permissions.get(
                tool_name,
                set(),
            )

        )



    # ======================================================
    # Query
    # ======================================================

    def permissions(
        self,
        tool_name: str,
    ) -> set[str]:
        """
        Return permission set.
        """

        return set(
            self._permissions.get(
                tool_name,
                set(),
            )
        )



    def list_permissions(
        self,
        tool_name: str,
    ) -> list[str]:
        """
        Return sorted permission list.

        Compatibility API.
        """

        return sorted(
            self.permissions(
                tool_name
            )
        )



    def has_permission(
        self,
        tool_name: str,
        permission: str,
    ) -> bool:
        """
        Direct permission lookup.
        """

        return permission in self._permissions.get(
            tool_name,
            set(),
        )



    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, list[str]]:
        """
        Export permissions.
        """

        return {

            tool:

            sorted(
                permissions
            )

            for tool, permissions
            in self._permissions.items()

        }



    def snapshot(
        self,
    ) -> dict[str, list[str]]:
        """
        Create state snapshot.
        """

        return self.to_dict()



    # ======================================================
    # Lifecycle
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all permissions.
        """

        self._permissions.clear()



    reset = clear



    # ======================================================
    # Properties
    # ======================================================

    @property
    def count(
        self,
    ) -> int:
        """
        Number of registered tools.
        """

        return len(
            self._permissions
        )



    # ======================================================
    # Python Protocols
    # ======================================================

    def __contains__(
        self,
        tool_name: str,
    ) -> bool:

        return tool_name in self._permissions



    def __len__(
        self,
    ) -> int:

        return len(
            self._permissions
        )



    def __bool__(
        self,
    ) -> bool:

        return bool(
            self._permissions
        )



    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"tools={len(self._permissions)}"

            ")"

        )