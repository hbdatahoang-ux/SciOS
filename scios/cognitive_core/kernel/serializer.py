"""
SciOS Kernel Serializer
=======================

Định nghĩa cơ chế import/export cho CognitiveRequest, CognitiveResponse, CognitiveContext.
Hỗ trợ JSON/YAML để dễ dàng lưu trữ, truyền qua network hoặc debug.
"""

import json
from typing import Any
from .request import CognitiveRequest
from .response import CognitiveResponse
from .context import CognitiveContext


class KernelSerializer:
    """
    KernelSerializer chuẩn hóa việc serialize/deserialize các đối tượng của Kernel.
    """

    # -----------------------------------------------------
    # Export
    # -----------------------------------------------------

    @staticmethod
    def to_json(obj: Any) -> str:
        """Serialize object thành JSON string."""
        if hasattr(obj, "to_dict"):
            return json.dumps(obj.to_dict(), ensure_ascii=False, indent=2)
        raise TypeError(f"Object {obj} không hỗ trợ to_dict()")

    @staticmethod
    def to_dict(obj: Any) -> dict:
        """Serialize object thành dict."""
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        raise TypeError(f"Object {obj} không hỗ trợ to_dict()")

    # -----------------------------------------------------
    # Import
    # -----------------------------------------------------

    @staticmethod
    def from_json_request(data: str) -> CognitiveRequest:
        """Deserialize JSON string thành CognitiveRequest."""
        payload = json.loads(data)
        return CognitiveRequest(
            request_id=payload["request_id"],
            query=payload["query"],
            inputs=payload.get("inputs", {}),
            metadata=payload.get("metadata", {}),
            created_at=payload.get("created_at"),
        )

    @staticmethod
    def from_json_response(data: str) -> CognitiveResponse:
        """Deserialize JSON string thành CognitiveResponse."""
        payload = json.loads(data)
        ctx = CognitiveContext(
            request=KernelSerializer.from_json_request(json.dumps(payload["context"]["request"]))
        )
        ctx.state = payload["context"].get("state", {})
        ctx.metadata = payload["context"].get("metadata", {})
        ctx.trace = payload["context"].get("trace", [])
        return CognitiveResponse(
            status=payload["status"],
            context=ctx,
            errors=payload.get("errors", []),
            warnings=payload.get("warnings", []),
            metadata=payload.get("metadata", {}),
        )
