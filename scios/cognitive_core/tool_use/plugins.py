# scios/cognitive_core/tool_use/plugins.py

"""
SciOS Plugin Loader
===================

Nạp các plugin tool bên ngoài vào ToolRegistry.
"""

import importlib
import pkgutil
from typing import List
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class PluginLoader:
    """
    PluginLoader chịu trách nhiệm tìm và nạp plugin tool.
    """

    def __init__(self, registry: ToolRegistry, plugin_package: str = "scios.plugins") -> None:
        self.registry = registry
        self.plugin_package = plugin_package

    def discover_plugins(self) -> List[str]:
        """
        Tìm tất cả module plugin trong package.
        """
        discovered = []
        package = importlib.import_module(self.plugin_package)
        for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if not ispkg:
                discovered.append(name)
        return discovered

    def load_plugins(self) -> None:
        """
        Nạp toàn bộ plugin và đăng ký tool vào registry.
        """
        for module_name in self.discover_plugins():
            module = importlib.import_module(module_name)
            # Mỗi plugin phải có hàm register_plugin(registry)
            if hasattr(module, "register_plugin"):
                module.register_plugin(self.registry)

    def load_plugin(self, module_name: str) -> None:
        """
        Nạp một plugin cụ thể.
        """
        module = importlib.import_module(module_name)
        if hasattr(module, "register_plugin"):
            module.register_plugin(self.registry)
