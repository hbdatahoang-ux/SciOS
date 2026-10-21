"""
SciOS Runtime Tool Policy
=========================

Security and execution policy for runtime tools.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
)


__all__ = [
    "ToolPolicy",
]



@dataclass(slots=True)
class ToolPolicy:
    """
    Security policy controlling tool execution.
    """



    # ======================================================
    # Tool Access
    # ======================================================


    allowed_tools: set[str] | None = None


    denied_tools: set[str] = field(
        default_factory=set
    )



    # ======================================================
    # Permissions
    # ======================================================


    permissions: set[str] = field(
        default_factory=set
    )



    # ======================================================
    # Execution Limits
    # ======================================================


    max_calls: int | None = None


    timeout_seconds: float = 30.0



    # ======================================================
    # Runtime State
    # ======================================================


    enabled: bool = True


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    _calls: int = field(
        default=0,
        init=False,
        repr=False,
    )



    # ======================================================
    # Tool Access API
    # ======================================================


    def allow_tool(
        self,
        name: str,
    ) -> None:
        """
        Add tool to allow list.
        """


        if self.allowed_tools is None:

            self.allowed_tools = set()


        self.allowed_tools.add(
            name
        )


        self.denied_tools.discard(
            name
        )



    def deny_tool(
        self,
        name: str,
    ) -> None:
        """
        Block a tool.
        """


        self.denied_tools.add(
            name
        )


        if self.allowed_tools:

            self.allowed_tools.discard(
                name
            )



    # ======================================================
    # Permission Check
    # ======================================================


    def can_execute(
        self,
        tool_name: str,
    ) -> bool:
        """
        Basic tool access check.
        """


        if not self.enabled:

            return False



        if tool_name in self.denied_tools:

            return False



        if self.allowed_tools is None:

            return True



        return (
            tool_name
            in
            self.allowed_tools
        )



    # ======================================================
    # Permission Model
    # ======================================================


    def grant(
        self,
        permission: str,
    ) -> None:

        self.permissions.add(
            permission
        )



    def revoke(
        self,
        permission: str,
    ) -> None:

        self.permissions.discard(
            permission
        )



    def has_permission(
        self,
        permission: str,
    ) -> bool:

        return (
            permission
            in
            self.permissions
        )



    # ======================================================
    # Limits
    # ======================================================


    def check_limit(
        self,
    ) -> bool:
        """
        Check execution quota.
        """


        if self.max_calls is None:

            return True


        return (
            self._calls
            <
            self.max_calls
        )



    def record_call(
        self,
    ) -> None:
        """
        Record successful authorization.
        """


        self._calls += 1



    def reset_calls(
        self,
    ) -> None:

        self._calls = 0



    @property
    def calls(
        self,
    ) -> int:

        return self._calls



    @property
    def remaining_calls(
        self,
    ) -> int | None:

        if self.max_calls is None:

            return None


        return max(
            0,
            self.max_calls - self._calls,
        )



    # ======================================================
    # Validation
    # ======================================================


    def validate(
        self,
        tool_name: str,
        *,
        permission: str | None = None,
    ) -> bool:
        """
        Full security validation.
        """


        if not self.can_execute(
            tool_name
        ):

            return False



        if not self.check_limit():

            return False



        if permission is not None:

            if not self.has_permission(
                permission
            ):

                return False



        return True



    # ======================================================
    # Compatibility API
    # ======================================================


    def allow(
        self,
        tool_name: str,
    ) -> bool:
        """
        Compatibility alias.
        """


        return self.validate(
            tool_name
        )



    # ======================================================
    # Lifecycle
    # ======================================================


    def enable(
        self,
    ) -> None:

        self.enabled = True



    def disable(
        self,
    ) -> None:

        self.enabled = False



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "enabled":
                self.enabled,


            "calls":
                self.calls,


            "remaining_calls":
                self.remaining_calls,


            "timeout_seconds":
                self.timeout_seconds,


            "allowed_tools":
                (
                    list(self.allowed_tools)
                    if self.allowed_tools
                    else None
                ),


            "denied_tools":
                list(
                    self.denied_tools
                ),

        }



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            **self.status(),


            "permissions":
                list(
                    self.permissions
                ),


            "max_calls":
                self.max_calls,


            "metadata":
                dict(
                    self.metadata
                ),

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (
            "ToolPolicy("
            f"enabled={self.enabled}, "
            f"calls={self.calls}"
            ")"
        )