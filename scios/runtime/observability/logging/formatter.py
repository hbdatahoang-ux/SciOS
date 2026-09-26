"""
SciOS-NG
runtime/observability/logging/formatter.py

Part 1. Foundation
"""


# =============================================================================
# Imports
# =============================================================================

from __future__ import annotations


import json
import uuid


from datetime import datetime
from datetime import timezone


from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional


from .record import LogRecord



# =============================================================================
# Constants
# =============================================================================

DEFAULT_FORMAT = (
    "[{level}] {message}"
)


DEFAULT_NAME = "default"



# =============================================================================
# Type Aliases
# =============================================================================

FormatContext = Dict[str, Any]

TemplateRegistry = Dict[str, str]

FormatterMetadata = Dict[str, Any]



# =============================================================================
# LogFormatter
# =============================================================================

class LogFormatter:
    """
    Structured log formatter.

    Responsible for transforming:

        LogRecord
              |
              ▼
        formatted output


    Supports:

    - text formatting
    - json formatting
    - templates
    - metadata
    - statistics
    """



    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(
        self,
        name: str = DEFAULT_NAME,
        *,
        template: str = DEFAULT_FORMAT,
        json_mode: bool = False,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """
        Initialize formatter.
        """


        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------

        self.id = str(
            uuid.uuid4()
        )

        self.name = name



        # ---------------------------------------------------------------------
        # Runtime State
        # ---------------------------------------------------------------------

        self.enabled = True

        self.created_at = datetime.now(
            timezone.utc
        )


        self.updated_at = self.created_at



        # ---------------------------------------------------------------------
        # Formatting Configuration
        # ---------------------------------------------------------------------

        self.template = template

        self.json_mode = json_mode



        # ---------------------------------------------------------------------
        # Template Registry
        # ---------------------------------------------------------------------

        self.templates: TemplateRegistry = {

            "default": DEFAULT_FORMAT,

            "simple":
                "{message}",

            "verbose":
                "[{timestamp}] "
                "[{level}] "
                "{source}: "
                "{message}",
        }



        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        self.metadata: FormatterMetadata = dict(
            metadata or {}
        )



        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------

        self.statistics = {

            "formatted": 0,

            "failed": 0,

            "json": 0,

        }
# =============================================================================
# Part 2. Properties
# =============================================================================


    # -------------------------------------------------------------------------
    # Identity Properties
    # -------------------------------------------------------------------------

    @property
    def id(
        self,
    ) -> str:
        """
        Return formatter unique identifier.
        """

        return self._id


    @id.setter
    def id(
        self,
        value: str,
    ) -> None:

        self._id = str(
            value
        )



    # -------------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Return formatter name.
        """

        return self._name


    @name.setter
    def name(
        self,
        value: str,
    ) -> None:

        self._name = str(
            value
        )



    # -------------------------------------------------------------------------
    # Formatting Properties
    # -------------------------------------------------------------------------

    @property
    def template(
        self,
    ) -> str:
        """
        Return current formatting template.
        """

        return self._template



    @template.setter
    def template(
        self,
        value: str,
    ) -> None:

        self._template = str(
            value
        )



    # -------------------------------------------------------------------------

    @property
    def json_mode(
        self,
    ) -> bool:
        """
        Return whether JSON formatting is enabled.
        """

        return self._json_mode



    @json_mode.setter
    def json_mode(
        self,
        value: bool,
    ) -> None:

        self._json_mode = bool(
            value
        )



    # -------------------------------------------------------------------------
    # Runtime State
    # -------------------------------------------------------------------------

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Return formatter active state.
        """

        return self._enabled



    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        self._enabled = bool(
            value
        )



    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> FormatterMetadata:
        """
        Return formatter metadata.
        """

        return self._metadata



    @metadata.setter
    def metadata(
        self,
        value: Mapping[str, Any],
    ) -> None:

        self._metadata = dict(
            value
        )



    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def statistics(
        self,
    ) -> Dict[str, int]:
        """
        Return formatter statistics.
        """

        return self._statistics



    @statistics.setter
    def statistics(
        self,
        value: Mapping[str, int],
    ) -> None:

        self._statistics = dict(
            value
        )



    # -------------------------------------------------------------------------
    # Runtime Information
    # -------------------------------------------------------------------------

    @property
    def age(
        self,
    ) -> float:
        """
        Return formatter lifetime in seconds.
        """

        now = datetime.now(
            timezone.utc
        )

        delta = (
            now
            -
            self.created_at
        )

        return delta.total_seconds()



    # -------------------------------------------------------------------------

    @property
    def format_count(
        self,
    ) -> int:
        """
        Return number of formatting operations.
        """

        return int(
            self.statistics.get(
                "formatted",
                0
            )
        )
# =============================================================================
# Part 3. Formatting API
# =============================================================================


    # -------------------------------------------------------------------------
    # Main Format Entry
    # -------------------------------------------------------------------------

    def format(
        self,
        record: LogRecord,
    ) -> str:
        """
        Format a LogRecord.

        Automatically selects:
        - JSON mode
        - Text mode
        """

        if not self.enabled:

            return ""


        try:

            if self.json_mode:

                result = self.format_json(
                    record
                )

            else:

                result = self.format_text(
                    record
                )


            self.statistics["formatted"] += 1

            self.updated_at = datetime.now(
                timezone.utc
            )

            return result


        except Exception:

            self.statistics["failed"] += 1

            return ""



    # -------------------------------------------------------------------------
    # Text Formatting
    # -------------------------------------------------------------------------

    def format_text(
        self,
        record: LogRecord,
    ) -> str:
        """
        Format record as plain text.
        """

        return self.format_template(
            record,
            self.template
        )



    # -------------------------------------------------------------------------
    # JSON Formatting
    # -------------------------------------------------------------------------

    def format_json(
        self,
        record: LogRecord,
    ) -> str:
        """
        Format record as JSON output.
        """

        self.statistics["json"] += 1


        return json.dumps(
            record.to_dict(),
            ensure_ascii=False,
            default=str,
        )



    # -------------------------------------------------------------------------
    # Record Formatting
    # -------------------------------------------------------------------------

    def format_record(
        self,
        record: LogRecord,
    ) -> Dict[str, Any]:
        """
        Convert record into structured format.
        """

        return record.to_dict()



    # -------------------------------------------------------------------------
    # Template Formatting
    # -------------------------------------------------------------------------

    def format_template(
        self,
        record: LogRecord,
        template: Optional[str] = None,
    ) -> str:
        """
        Apply template to LogRecord.
        """

        template = (
            template
            or
            self.template
        )


        return self.apply_template(
            template,
            record
        )



    # -------------------------------------------------------------------------

    def apply_template(
        self,
        template: str,
        record: LogRecord,
    ) -> str:
        """
        Render template variables.

        Supported:

        {id}
        {timestamp}
        {level}
        {source}
        {message}
        """

        values = {

            "id":
                record.id,

            "timestamp":
                record.timestamp.isoformat(),

            "level":
                record.level.name,

            "source":
                record.source,

            "message":
                record.message,

            "context":
                record.context,

        }


        return template.format(
            **values
        )



    # -------------------------------------------------------------------------
    # Render API
    # -------------------------------------------------------------------------

    def render(
        self,
        record: LogRecord,
        *,
        template: Optional[str] = None,
    ) -> str:
        """
        Render record with optional template.
        """

        if template:

            return self.format_template(
                record,
                template
            )


        return self.format(
            record
        )



    # -------------------------------------------------------------------------
    # Preview API
    # -------------------------------------------------------------------------

    def preview(
        self,
        record: LogRecord,
    ) -> str:
        """
        Preview formatting result.

        Does not update statistics.
        """

        if self.json_mode:

            return json.dumps(
                record.to_dict(),
                ensure_ascii=False,
                default=str,
            )


        return self.apply_template(
            self.template,
            record
        )
# =============================================================================
# Part 4. Template Registry API
# =============================================================================


    # -------------------------------------------------------------------------
    # Add Template
    # -------------------------------------------------------------------------

    def add_template(
        self,
        name: str,
        template: str,
    ) -> "LogFormatter":
        """
        Register a new formatting template.
        """

        if not name:
            raise ValueError(
                "Template name cannot be empty."
            )

        if not isinstance(
            template,
            str,
        ):
            raise TypeError(
                "Template must be a string."
            )


        self.templates[name] = template


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Template
    # -------------------------------------------------------------------------

    def remove_template(
        self,
        name: str,
    ) -> bool:
        """
        Remove template from registry.
        """

        if name not in self.templates:

            return False


        del self.templates[name]


        self.updated_at = datetime.now(
            timezone.utc
        )


        return True



    # -------------------------------------------------------------------------
    # Get Template
    # -------------------------------------------------------------------------

    def template(
        self,
        name: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve template by name.
        """

        return self.templates.get(
            name,
            default,
        )



    # -------------------------------------------------------------------------
    # List Templates
    # -------------------------------------------------------------------------

    def templates(
        self,
    ) -> Dict[str, str]:
        """
        Return all registered templates.
        """

        return dict(
            self.templates
        )



    # -------------------------------------------------------------------------
    # Check Template
    # -------------------------------------------------------------------------

    def has_template(
        self,
        name: str,
    ) -> bool:
        """
        Check whether template exists.
        """

        return name in self.templates



    # -------------------------------------------------------------------------
    # Activate Template
    # -------------------------------------------------------------------------

    def use_template(
        self,
        name: str,
    ) -> "LogFormatter":
        """
        Switch current active template.
        """

        if name not in self.templates:

            raise KeyError(
                f"Template '{name}' not found."
            )


        self.template = self.templates[name]


        self.metadata["active_template"] = name


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Default Template
    # -------------------------------------------------------------------------

    def default_template(
        self,
    ) -> str:
        """
        Return default template.
        """

        return self.templates.get(
            "default",
            DEFAULT_FORMAT,
        )



    # -------------------------------------------------------------------------
    # Clear Registry
    # -------------------------------------------------------------------------

    def clear_templates(
        self,
    ) -> "LogFormatter":
        """
        Clear all templates and restore defaults.
        """

        self.templates.clear()


        self.templates.update(
            {
                "default":
                    DEFAULT_FORMAT,

                "simple":
                    "{message}",

                "verbose":
                    "[{timestamp}] "
                    "[{level}] "
                    "{source}: "
                    "{message}",
            }
        )


        self.template = DEFAULT_FORMAT


        return self



    # -------------------------------------------------------------------------
    # Template Count
    # -------------------------------------------------------------------------

    def template_count(
        self,
    ) -> int:
        """
        Return number of registered templates.
        """

        return len(
            self.templates
        )
# =============================================================================
# Part 5. Lifecycle API
# =============================================================================


    # -------------------------------------------------------------------------
    # Enable
    # -------------------------------------------------------------------------

    def enable(
        self,
    ) -> "LogFormatter":
        """
        Enable formatter.
        """

        self.enabled = True

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self



    # -------------------------------------------------------------------------
    # Disable
    # -------------------------------------------------------------------------

    def disable(
        self,
    ) -> "LogFormatter":
        """
        Disable formatter.
        """

        self.enabled = False

        self.updated_at = datetime.now(
            timezone.utc
        )

        return self



    # -------------------------------------------------------------------------
    # Reset
    # -------------------------------------------------------------------------

    def reset(
        self,
    ) -> "LogFormatter":
        """
        Reset formatter runtime state.

        Keeps:
        - identity
        - metadata
        - templates
        """

        self.enabled = True

        self.template = DEFAULT_FORMAT

        self.json_mode = False


        self.statistics.clear()

        self.statistics.update(
            {
                "formatted": 0,
                "failed": 0,
                "json": 0,
            }
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------------------

    def clear(
        self,
    ) -> "LogFormatter":
        """
        Clear runtime data.

        Removes:
        - metadata
        - statistics
        - active configuration
        """

        self.metadata.clear()


        self.statistics.clear()


        self.template = DEFAULT_FORMAT

        self.json_mode = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Freeze
    # -------------------------------------------------------------------------

    def freeze(
        self,
    ) -> "LogFormatter":
        """
        Freeze formatter configuration.

        Frozen formatter cannot be modified.
        """

        self._frozen = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Unfreeze
    # -------------------------------------------------------------------------

    def unfreeze(
        self,
    ) -> "LogFormatter":
        """
        Unfreeze formatter.
        """

        self._frozen = False


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Close
    # -------------------------------------------------------------------------

    def close(
        self,
    ) -> "LogFormatter":
        """
        Close formatter lifecycle.
        """

        self.enabled = False

        self._closed = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Reopen
    # -------------------------------------------------------------------------

    def reopen(
        self,
    ) -> "LogFormatter":
        """
        Reopen closed formatter.
        """

        self._closed = False

        self.enabled = True


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self
# =============================================================================
# Part 6. Runtime Operations
# =============================================================================


    # -------------------------------------------------------------------------
    # Snapshot
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create formatter runtime snapshot.

        Includes:
        - configuration
        - templates
        - metadata
        - statistics
        - lifecycle state
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "template":
                self.template,

            "json_mode":
                self.json_mode,

            "enabled":
                self.enabled,

            "frozen":
                getattr(
                    self,
                    "_frozen",
                    False
                ),

            "closed":
                getattr(
                    self,
                    "_closed",
                    False
                ),

            "templates":
                dict(
                    self.templates
                ),

            "metadata":
                dict(
                    self.metadata
                ),

            "statistics":
                dict(
                    self.statistics
                ),

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),
        }



    # -------------------------------------------------------------------------
    # Restore
    # -------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "LogFormatter":
        """
        Restore formatter from snapshot.
        """

        self.name = snapshot.get(
            "name",
            self.name
        )


        self.template = snapshot.get(
            "template",
            DEFAULT_FORMAT
        )


        self.json_mode = snapshot.get(
            "json_mode",
            False
        )


        self.enabled = snapshot.get(
            "enabled",
            True
        )


        self._frozen = snapshot.get(
            "frozen",
            False
        )


        self._closed = snapshot.get(
            "closed",
            False
        )


        self.templates.clear()

        self.templates.update(
            snapshot.get(
                "templates",
                {}
            )
        )


        self.metadata.clear()

        self.metadata.update(
            snapshot.get(
                "metadata",
                {}
            )
        )


        self.statistics.clear()

        self.statistics.update(
            snapshot.get(
                "statistics",
                {}
            )
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Clone
    # -------------------------------------------------------------------------

    def clone(
        self,
    ) -> "LogFormatter":
        """
        Create independent formatter copy.
        """

        formatter = LogFormatter(
            name=self.name,
            template=self.template,
            json_mode=self.json_mode,
            metadata=self.metadata,
        )


        formatter.templates.update(
            self.templates
        )


        formatter.statistics.update(
            self.statistics
        )


        formatter.enabled = self.enabled

        formatter._frozen = getattr(
            self,
            "_frozen",
            False
        )

        formatter._closed = getattr(
            self,
            "_closed",
            False
        )


        return formatter



    # -------------------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------------------

    def copy(
        self,
    ) -> "LogFormatter":
        """
        Alias for clone().
        """

        return self.clone()



    # -------------------------------------------------------------------------
    # Optimize
    # -------------------------------------------------------------------------

    def optimize(
        self,
    ) -> "LogFormatter":
        """
        Optimize formatter runtime.

        Actions:
        - remove invalid templates
        - normalize metadata
        - cleanup statistics
        """

        invalid = []

        for name, template in self.templates.items():

            if not isinstance(
                template,
                str
            ):

                invalid.append(
                    name
                )


        for name in invalid:

            del self.templates[name]


        self.metadata = dict(
            self.metadata
        )


        self.statistics = {

            key: int(value)

            for key, value
            in self.statistics.items()

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "LogFormatter":
        """
        Remove unused runtime resources.
        """

        self.metadata.clear()


        self.statistics = {

            "formatted": 0,

            "failed": 0,

            "json": 0,

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self



    # -------------------------------------------------------------------------
    # Compact
    # -------------------------------------------------------------------------

    def compact(
        self,
    ) -> "LogFormatter":
        """
        Compact formatter memory state.

        Removes empty metadata entries.
        """

        self.metadata = {

            key: value

            for key, value
            in self.metadata.items()

            if value is not None

        }


        self.updated_at = datetime.now(
            timezone.utc
        )


        return self
# =============================================================================
# Part 7. Statistics & Diagnostics
# =============================================================================


    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return formatter summary.
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "enabled":
                self.enabled,

            "json_mode":
                self.json_mode,

            "template":
                self.template,

            "templates":
                self.template_count,

            "formatted":
                self.format_count,

            "errors":
                self.error_count,

            "uptime":
                self.uptime,

            "latency":
                self.latency,

        }



    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate detailed diagnostic report.
        """

        return {

            "identity": {

                "id":
                    self.id,

                "name":
                    self.name,

            },


            "state": {

                "enabled":
                    self.enabled,

                "frozen":
                    getattr(
                        self,
                        "_frozen",
                        False
                    ),

                "closed":
                    getattr(
                        self,
                        "_closed",
                        False
                    ),

            },


            "configuration": {

                "template":
                    self.template,

                "json_mode":
                    self.json_mode,

                "template_count":
                    self.template_count,

            },


            "statistics":
                dict(
                    self.statistics
                ),


            "performance": {

                "uptime":
                    self.uptime,

                "latency":
                    self.latency,

            },

        }



    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Check formatter health state.
        """

        healthy = (

            self.enabled

            and

            not getattr(
                self,
                "_closed",
                False
            )

        )


        return {

            "healthy":
                healthy,

            "status":
                "ok"
                if healthy
                else
                "inactive",


            "errors":
                self.error_count,

        }



    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def status(
        self,
    ) -> str:
        """
        Return formatter status.
        """

        if getattr(
            self,
            "_closed",
            False
        ):

            return "closed"


        if getattr(
            self,
            "_frozen",
            False
        ):

            return "frozen"


        if self.enabled:

            return "active"


        return "disabled"



    # -------------------------------------------------------------------------
    # Template Count
    # -------------------------------------------------------------------------

    @property
    def template_count(
        self,
    ) -> int:
        """
        Return number of registered templates.
        """

        return len(
            self.templates
        )



    # -------------------------------------------------------------------------
    # Format Count
    # -------------------------------------------------------------------------

    @property
    def format_count(
        self,
    ) -> int:
        """
        Return successful formatting count.
        """

        return int(
            self.statistics.get(
                "formatted",
                0
            )
        )



    # -------------------------------------------------------------------------
    # Error Count
    # -------------------------------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:
        """
        Return formatting error count.
        """

        return int(
            self.statistics.get(
                "failed",
                0
            )
        )



    # -------------------------------------------------------------------------
    # Uptime
    # -------------------------------------------------------------------------

    @property
    def uptime(
        self,
    ) -> float:
        """
        Return formatter uptime seconds.
        """

        now = datetime.now(
            timezone.utc
        )


        return (
            now
            -
            self.created_at
        ).total_seconds()



    # -------------------------------------------------------------------------
    # Latency
    # -------------------------------------------------------------------------

    @property
    def latency(
        self,
    ) -> float:
        """
        Estimate average formatting latency.

        Unit:
            milliseconds
        """

        count = self.format_count


        if count == 0:

            return 0.0


        total = self.statistics.get(
            "total_time",
            0.0
        )


        return (
            total
            /
            count
        ) * 1000
# =============================================================================
# Part 8. Serialization
# =============================================================================


    # -------------------------------------------------------------------------
    # To Dictionary
    # -------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert formatter into dictionary representation.
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "template":
                self.template,

            "json_mode":
                self.json_mode,

            "enabled":
                self.enabled,

            "frozen":
                getattr(
                    self,
                    "_frozen",
                    False
                ),

            "closed":
                getattr(
                    self,
                    "_closed",
                    False
                ),

            "templates":
                dict(
                    self.templates
                ),

            "metadata":
                dict(
                    self.metadata
                ),

            "statistics":
                dict(
                    self.statistics
                ),

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),

        }



    # -------------------------------------------------------------------------
    # From Dictionary
    # -------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "LogFormatter":
        """
        Create formatter from dictionary.
        """

        formatter = cls(
            name=data.get(
                "name",
                DEFAULT_NAME
            ),

            template=data.get(
                "template",
                DEFAULT_FORMAT
            ),

            json_mode=data.get(
                "json_mode",
                False
            ),

            metadata=data.get(
                "metadata",
                {}
            ),
        )


        formatter.enabled = data.get(
            "enabled",
            True
        )


        formatter._frozen = data.get(
            "frozen",
            False
        )


        formatter._closed = data.get(
            "closed",
            False
        )


        formatter.templates.update(
            data.get(
                "templates",
                {}
            )
        )


        formatter.statistics.update(
            data.get(
                "statistics",
                {}
            )
        )


        return formatter



    # -------------------------------------------------------------------------
    # To JSON
    # -------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize formatter into JSON string.
        """

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent,
            default=str,
        )



    # -------------------------------------------------------------------------
    # From JSON
    # -------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "LogFormatter":
        """
        Create formatter from JSON string.
        """

        data = json.loads(
            value
        )


        return cls.from_dict(
            data
        )



    # -------------------------------------------------------------------------
    # Serialize
    # -------------------------------------------------------------------------

    def serialize(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime serialization.

        Alias of to_dict().
        """

        return self.to_dict()



    # -------------------------------------------------------------------------
    # Deserialize
    # -------------------------------------------------------------------------

    def deserialize(
        self,
        data: Mapping[str, Any],
    ) -> "LogFormatter":
        """
        Restore formatter state.
        """

        restored = self.from_dict(
            data
        )


        self.restore(
            restored.to_dict()
        )


        return self
# =============================================================================
# Part 9. Events & Hooks
# =============================================================================


    # -------------------------------------------------------------------------
    # Before Format
    # -------------------------------------------------------------------------

    def before_format(
        self,
        record: LogRecord,
    ) -> None:
        """
        Trigger before formatting record.
        """

        self.emit(
            "before_format",
            formatter=self,
            record=record,
        )



    # -------------------------------------------------------------------------
    # After Format
    # -------------------------------------------------------------------------

    def after_format(
        self,
        record: LogRecord,
        result: str,
    ) -> None:
        """
        Trigger after formatting record.
        """

        self.emit(
            "after_format",
            formatter=self,
            record=record,
            result=result,
        )



    # -------------------------------------------------------------------------
    # Before Template
    # -------------------------------------------------------------------------

    def before_template(
        self,
        template: str,
        record: LogRecord,
    ) -> None:
        """
        Trigger before template rendering.
        """

        self.emit(
            "before_template",
            formatter=self,
            template=template,
            record=record,
        )



    # -------------------------------------------------------------------------
    # After Template
    # -------------------------------------------------------------------------

    def after_template(
        self,
        template: str,
        result: str,
    ) -> None:
        """
        Trigger after template rendering.
        """

        self.emit(
            "after_template",
            formatter=self,
            template=template,
            result=result,
        )



    # -------------------------------------------------------------------------
    # Add Hook
    # -------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        callback,
    ) -> "LogFormatter":
        """
        Register event callback.
        """

        if not hasattr(
            self,
            "_hooks",
        ):

            self._hooks = {}


        if event not in self._hooks:

            self._hooks[event] = []


        self._hooks[event].append(
            callback
        )


        return self



    # -------------------------------------------------------------------------
    # Remove Hook
    # -------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        callback,
    ) -> bool:
        """
        Remove event callback.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )


        if event not in hooks:

            return False


        if callback not in hooks[event]:

            return False


        hooks[event].remove(
            callback
        )


        return True



    # -------------------------------------------------------------------------
    # Emit
    # -------------------------------------------------------------------------

    def emit(
        self,
        event: str,
        **payload,
    ) -> None:
        """
        Dispatch formatter event.
        """

        hooks = getattr(
            self,
            "_hooks",
            {},
        )


        callbacks = hooks.get(
            event,
            [],
        )


        for callback in list(callbacks):

            try:

                callback(
                    **payload
                )

            except Exception:

                # Observability hooks
                # must not break logging.
                continue



    # -------------------------------------------------------------------------
    # Subscribe
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        callback,
    ) -> "LogFormatter":
        """
        Subscribe to formatter event.

        Alias for add_hook().
        """

        return self.add_hook(
            event,
            callback,
        )
# =============================================================================
# Part 10. Python Protocols
# =============================================================================


    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"LogFormatter("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"enabled={self.enabled!r}, "
            f"json_mode={self.json_mode!r}"
            f")"
        )



    # -------------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"Formatter<{self.name}> "
            f"[{self.status()}]"
        )



    # -------------------------------------------------------------------------
    # Collection Protocols
    # -------------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of registered templates.
        """

        return self.template_count



    # -------------------------------------------------------------------------

    def __iter__(
        self,
    ):
        """
        Iterate through templates.
        """

        return iter(
            self.templates.items()
        )



    # -------------------------------------------------------------------------

    def __contains__(
        self,
        item: str,
    ) -> bool:
        """
        Check template existence.
        """

        return self.has_template(
            item
        )



    # -------------------------------------------------------------------------
    # Callable Protocol
    # -------------------------------------------------------------------------

    def __call__(
        self,
        record: LogRecord,
    ) -> str:
        """
        Allow formatter(record) syntax.
        """

        return self.format(
            record
        )



    # -------------------------------------------------------------------------
    # Copy Protocol
    # -------------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "LogFormatter":
        """
        Shallow copy.
        """

        return self.clone()



    # -------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ) -> "LogFormatter":
        """
        Deep copy.
        """

        formatter = self.clone()


        memo[id(self)] = formatter


        return formatter                                                                        