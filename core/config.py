# Configuration management for macro settings
import os
import yaml
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.macro_imba/config.yaml")


class MacroConfig:
    """Configuration manager for macro settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.settings: Dict[str, Any] = self._get_default_settings()
        self._ensure_config_dir()
        
    def _ensure_config_dir(self) -> bool:
        """Create config directory if it doesn't exist."""
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
                return True
            except (OSError, PermissionError):
                return False
        return True
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        return {
            "quick_cast": {
                "enabled": True,
                "hotkeys": {
                    "skill_1": "q",
                    "skill_2": "w",
                    "skill_3": "e",
                    "skill_4": "r",
                    "skill_5": "d",
                    "skill_6": "f"
                }
            },
            "auto_cast": {
                "enabled": False,
                "skills": [],
                "interval_ms": 100
            },
            "macros": [],
            "global_hotkey": "f9",
            "toggle_enabled": True
        }
    
    def load(self) -> bool:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            return False
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    self.settings.update(loaded)
            return True
        except (yaml.YAMLError, IOError):
            return False
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            self._ensure_config_dir()
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.settings, f, default_flow_style=False, allow_unicode=True)
            return True
        except IOError:
            return False
    
    def get_quick_cast_enabled(self) -> bool:
        """Check if quick-cast is enabled."""
        return self.settings.get("quick_cast", {}).get("enabled", True)
    
    def set_quick_cast_enabled(self, enabled: bool) -> None:
        """Set quick-cast enabled state."""
        if "quick_cast" not in self.settings:
            self.settings["quick_cast"] = {}
        self.settings["quick_cast"]["enabled"] = enabled
    
    def get_quick_cast_hotkeys(self) -> Dict[str, str]:
        """Get quick-cast hotkey mappings."""
        return self.settings.get("quick_cast", {}).get("hotkeys", {})
    
    def set_quick_cast_hotkey(self, skill_name: str, hotkey: str) -> None:
        """Set a quick-cast hotkey for a skill."""
        if "quick_cast" not in self.settings:
            self.settings["quick_cast"] = {}
        if "hotkeys" not in self.settings["quick_cast"]:
            self.settings["quick_cast"]["hotkeys"] = {}
        self.settings["quick_cast"]["hotkeys"][skill_name] = hotkey
    
    def get_auto_cast_enabled(self) -> bool:
        """Check if auto-cast is enabled."""
        return self.settings.get("auto_cast", {}).get("enabled", False)
    
    def set_auto_cast_enabled(self, enabled: bool) -> None:
        """Set auto-cast enabled state."""
        if "auto_cast" not in self.settings:
            self.settings["auto_cast"] = {}
        self.settings["auto_cast"]["enabled"] = enabled
    
    def get_auto_cast_skills(self) -> List[Dict[str, Any]]:
        """Get list of skills configured for auto-cast."""
        return self.settings.get("auto_cast", {}).get("skills", [])
    
    def add_auto_cast_skill(self, skill: Dict[str, Any]) -> None:
        """Add a skill to auto-cast list."""
        if "auto_cast" not in self.settings:
            self.settings["auto_cast"] = {}
        if "skills" not in self.settings["auto_cast"]:
            self.settings["auto_cast"]["skills"] = []
        self.settings["auto_cast"]["skills"].append(skill)
    
    def remove_auto_cast_skill(self, skill_hotkey: str) -> bool:
        """Remove a skill from auto-cast list by hotkey."""
        skills = self.get_auto_cast_skills()
        for i, skill in enumerate(skills):
            if skill.get("hotkey") == skill_hotkey:
                skills.pop(i)
                return True
        return False
    
    def get_macros(self) -> List[Dict[str, Any]]:
        """Get list of custom macros."""
        return self.settings.get("macros", [])
    
    def add_macro(self, macro: Dict[str, Any]) -> None:
        """Add a custom macro."""
        if "macros" not in self.settings:
            self.settings["macros"] = []
        self.settings["macros"].append(macro)
    
    def remove_macro(self, macro_name: str) -> bool:
        """Remove a macro by name."""
        macros = self.get_macros()
        for i, macro in enumerate(macros):
            if macro.get("name") == macro_name:
                macros.pop(i)
                return True
        return False
    
    def get_global_hotkey(self) -> str:
        """Get the global toggle hotkey."""
        return self.settings.get("global_hotkey", "f9")
    
    def set_global_hotkey(self, hotkey: str) -> None:
        """Set the global toggle hotkey."""
        self.settings["global_hotkey"] = hotkey
