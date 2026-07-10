"""
SciOS Tool Adapters
===================

Kết nối và chuyển đổi dữ liệu giữa ToolRequest/ToolResponse và hệ thống bên ngoài:
- RequestAdapter: ToolRequest <-> dict
- ResponseAdapter: ToolResponse <-> dict
- ExternalAdapter: REST API adapter
- AdapterRegistry: quản lý adapter bên ngoài
"""

import requests
from typing import Dict, Any, Optional
from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.response import ToolResponse


class RequestAdapter:
    """Chuyển đổi ToolRequest <-> dict."""

    def to_dict(self, request: ToolRequest) -> Dict[str, Any]:
        return {
            "tool": request.tool,
            "action": request.action,
            "params": request.params,
        }

    def from_dict(self, data: Dict[str, Any]) -> ToolRequest:
        if "tool" not in data or "action" not in data or "params" not in data:
            raise ValueError("Invalid request dict")
        return ToolRequest(tool=data["tool"], action=data["action"], params=data["params"])

    def __repr__(self) -> str:
        return "<RequestAdapter>"


class ResponseAdapter:
    """Chuyển đổi ToolResponse <-> dict."""

    def to_dict(self, response: ToolResponse) -> Dict[str, Any]:
        return {
            "tool": response.tool,
            "status": response.status,
            "result": response.result,
            "message": response.message,
        }

    def from_dict(self, data: Dict[str, Any]) -> ToolResponse:
        if "tool" not in data or "status" not in data:
            raise ValueError("Invalid response dict")
        return ToolResponse(
            tool=data["tool"],
            status=data["status"],
            result=data.get("result"),
            message=data.get("message"),
        )

    def __repr__(self) -> str:
        return "<ResponseAdapter>"


class ExternalAdapter:
    """Adapter kết nối REST API bên ngoài."""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None) -> None:
        self.base_url = base_url
        self.headers = headers or {}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=self.headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(f"{self.base_url}/{endpoint}", json=data, headers=self.headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class AdapterRegistry:
    """Quản lý danh sách adapter bên ngoài."""

    def __init__(self) -> None:
        self.adapters: Dict[str, ExternalAdapter] = {}

    def register(self, name: str, adapter: ExternalAdapter) -> None:
        self.adapters[name] = adapter

    def get(self, name: str) -> Optional[ExternalAdapter]:
        return self.adapters.get(name)

    def list_adapters(self) -> Dict[str, str]:
        return {name: adapter.base_url for name, adapter in self.adapters.items()}
