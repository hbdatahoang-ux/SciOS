"""
SciOS Kernel Serializer
=======================

Định nghĩa cơ chế import/export cho:

- CognitiveRequest
- CognitiveResponse
- CognitiveContext

Hỗ trợ JSON serialization/deserialization với các kiểu dữ liệu
thường dùng trong Cognitive Kernel như UUID và datetime.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from .context import CognitiveContext
from .request import CognitiveRequest
from .response import CognitiveResponse


class KernelSerializer:
    """
    Chuẩn hóa serialize/deserialize các đối tượng của Cognitive Kernel.

    Contract:
        object -> dict -> JSON -> dict -> object

    Các kiểu dữ liệu đặc biệt:
        UUID     -> str
        datetime -> ISO-8601 str
    """

    # ------------------------------------------------------------------
    # JSON helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _json_default(obj: Any) -> Any:
        """
        Convert các kiểu Python không được json.dumps hỗ trợ mặc định.
        """
        if isinstance(obj, (datetime, UUID)):
            return str(obj) if isinstance(obj, UUID) else obj.isoformat()

        raise TypeError(
            f"Object of type {type(obj).__name__} is not JSON serializable"
        )

    @staticmethod
    def _parse_datetime(value: Any) -> Any:
        """
        Khôi phục datetime từ ISO-8601 string.

        Nếu value không phải string hoặc không parse được,
        giữ nguyên value để đảm bảo backward compatibility.
        """
        if value is None or isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value

        return value

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    @staticmethod
    def to_dict(obj: Any) -> dict:
        """
        Serialize object thành dictionary.

        Object phải cung cấp public ``to_dict()``.
        """
        if not hasattr(obj, "to_dict"):
            raise TypeError(
                f"Object {obj!r} không hỗ trợ to_dict()"
            )

        result = obj.to_dict()

        if not isinstance(result, dict):
            raise TypeError(
                f"{type(obj).__name__}.to_dict() phải trả về dict, "
                f"nhận được {type(result).__name__}"
            )

        return result

    @staticmethod
    def to_json(obj: Any) -> str:
        """
        Serialize object thành pretty JSON string.

        Unicode được giữ nguyên và datetime/UUID được chuyển
        sang representation JSON-compatible.
        """
        return json.dumps(
            KernelSerializer.to_dict(obj),
            ensure_ascii=False,
            indent=2,
            default=KernelSerializer._json_default,
        )

    # ------------------------------------------------------------------
    # Import: Request
    # ------------------------------------------------------------------

    @staticmethod
    def from_json_request(data: str) -> CognitiveRequest:
        """
        Deserialize JSON string thành CognitiveRequest.
        """
        payload = json.loads(data)

        if not isinstance(payload, dict):
            raise TypeError("Request JSON phải deserialize thành dict")

        return CognitiveRequest(
            request_id=payload["request_id"],
            query=payload["query"],
            inputs=payload.get("inputs", {}),
            metadata=payload.get("metadata", {}),
            created_at=KernelSerializer._parse_datetime(
                payload.get("created_at")
            ),
        )

    # ------------------------------------------------------------------
    # Import: Context
    # ------------------------------------------------------------------

    @staticmethod
    def from_dict_context(payload: dict) -> CognitiveContext:
        """
        Khôi phục CognitiveContext từ dictionary.
        """
        if not isinstance(payload, dict):
            raise TypeError("Context payload phải là dict")

        request_payload = payload.get("request")

        if not isinstance(request_payload, dict):
            raise ValueError(
                "Context payload phải chứa request dạng dict"
            )

        request = KernelSerializer.from_dict_request(request_payload)

        context = CognitiveContext(request)

        context.state = dict(
            payload.get("state", {})
        )

        context.metadata = dict(
            payload.get("metadata", {})
        )

        context.trace = list(
            payload.get("trace", [])
        )

        return context

    @staticmethod
    def from_dict_request(payload: dict) -> CognitiveRequest:
        """
        Khôi phục CognitiveRequest từ dictionary.
        """
        if not isinstance(payload, dict):
            raise TypeError("Request payload phải là dict")

        return CognitiveRequest(
            request_id=payload["request_id"],
            query=payload["query"],
            inputs=payload.get("inputs", {}),
            metadata=payload.get("metadata", {}),
            created_at=KernelSerializer._parse_datetime(
                payload.get("created_at")
            ),
        )

    # ------------------------------------------------------------------
    # Import: Response
    # ------------------------------------------------------------------

    @staticmethod
    def from_json_response(data: str) -> CognitiveResponse:
        """
        Deserialize JSON string thành CognitiveResponse.

        Contract:
        - JSON phải deserialize thành dict.
        - ``context`` là field bắt buộc.
        - ``status`` là field bắt buộc.
        - ``context`` phải là dict.
        """
        payload = json.loads(data)

        if not isinstance(payload, dict):
            raise TypeError(
                "Response JSON phải deserialize thành dict"
            )

        # Required fields: để KeyError nổi lên đúng contract.
        context_payload = payload["context"]
        status = payload["status"]

        if not isinstance(context_payload, dict):
            raise ValueError(
                "Response payload phải chứa context dạng dict"
            )

        context = KernelSerializer.from_dict_context(context_payload)

        return CognitiveResponse(
            status=status,
            context=context,
            errors=payload.get("errors", []),
            warnings=payload.get("warnings", []),
            metadata=payload.get("metadata", {}),
        )


# ----------------------------------------------------------------------
# Backward-compatible public alias
# ----------------------------------------------------------------------

CognitiveSerializer = KernelSerializer


__all__ = [
    "KernelSerializer",
    "CognitiveSerializer",
]