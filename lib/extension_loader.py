"""
ThinkTank Demo - Extension Loader
Simple extension system for domain expertise
"""

import json
import os
from pathlib import Path


class ExtensionLoader:
    """
    Loads and manages domain extensions that enhance agent expertise.
    """

    def __init__(self, extensions_path="extensions"):
        """
        Initialize extension loader.

        Args:
            extensions_path: Path to extensions directory
        """
        self.extensions_path = extensions_path
        self.loaded_extensions = {}

    def load_extensions(self):
        """
        Load all available extensions from the extensions directory.

        Returns:
            dict: Mapping of extension names to their configurations
        """
        if not os.path.exists(self.extensions_path):
            return {}

        for ext_dir in Path(self.extensions_path).iterdir():
            if ext_dir.is_dir():
                config_file = ext_dir / "extension.json"
                if config_file.exists():
                    try:
                        with open(config_file, "r") as f:
                            config = json.load(f)
                            ext_name = config.get("name", ext_dir.name)
                            self.loaded_extensions[ext_name] = {
                                "config": config,
                                "path": ext_dir
                            }
                    except Exception as e:
                        print(f"[Warning] Failed to load extension {ext_dir.name}: {e}")

        return self.loaded_extensions

    def get_extension_context(self, prompt):
        """
        Get relevant extension context based on prompt.

        Args:
            prompt: User's question/task

        Returns:
            str: Extension context to inject, or None if no match
        """
        prompt_lower = prompt.lower()

        # Check each extension's keywords
        for ext_name, ext_data in self.loaded_extensions.items():
            config = ext_data["config"]
            keywords = config.get("keywords", [])

            # Check if any keyword matches
            if any(keyword.lower() in prompt_lower for keyword in keywords):
                # Load system prompt
                system_prompt_file = ext_data["path"] / "system_prompt.txt"
                if system_prompt_file.exists():
                    with open(system_prompt_file, "r") as f:
                        context = f.read()
                        return f"\n=== {config.get('display_name', ext_name)} Expertise ===\n{context}"

        return None

    def list_extensions(self):
        """
        List all loaded extensions.

        Returns:
            list: List of extension names
        """
        return list(self.loaded_extensions.keys())
