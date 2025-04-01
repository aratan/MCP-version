import json
from typing import Dict, Any, Callable, Optional

class FunctionManager:
    def __init__(self):
        self.available_functions: Dict[str, Callable] = {}
        self.alias_map: Dict[str, list] = {}
        self.param_map: Dict[str, dict] = {}

    def load_config(self, config_path: str) -> None:
        """Load function configuration from JSON file."""
        with open(config_path, 'r') as f:
            self.tools_config = json.load(f)

    def register_function(self, name: str, func: Callable) -> None:
        """Register a function with its configuration."""
        self.available_functions[name] = func

    def resolve_alias(self, function_name: str) -> Optional[str]:
        """Resolve function alias to canonical name."""
        # Check if it's a direct match first
        if function_name in self.available_functions:
            return function_name
            
        # Then check aliases
        return next(
            (canonical for canonical, aliases in self.alias_map.items()
             if function_name.lower() in [alias.lower() for alias in aliases]),
            None
        )

    def setup_functions(self, functions_module, enabled_functions: list = None) -> None:
        """Setup functions from configuration."""
        for tool in self.tools_config:
            function_name = tool["name"]
            if hasattr(functions_module, function_name):
                self.available_functions[function_name] = getattr(functions_module, function_name)
                self.alias_map[function_name] = [function_name] + tool.get("aliases", [])  # Include the canonical name in aliases
                self.param_map[function_name] = tool.get("param_maps", {})

        if enabled_functions:
            enabled_functions = [f.strip() for f in enabled_functions if f.strip()]
            self.available_functions = {
                name: func for name, func in self.available_functions.items()
                if name in enabled_functions
            }
