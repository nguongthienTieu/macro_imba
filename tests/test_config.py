"""Tests for the MacroConfig class."""
import os
import tempfile
import pytest

from core.config import MacroConfig


class TestMacroConfig:
    """Test cases for MacroConfig."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")
        self.config = MacroConfig(self.config_path)
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_default_settings(self):
        """Test that default settings are loaded."""
        assert self.config.get_quick_cast_enabled() is True
        assert self.config.get_auto_cast_enabled() is False
        assert "skill_1" in self.config.get_quick_cast_hotkeys()
    
    def test_set_quick_cast_enabled(self):
        """Test setting quick-cast enabled state."""
        self.config.set_quick_cast_enabled(False)
        assert self.config.get_quick_cast_enabled() is False
        
        self.config.set_quick_cast_enabled(True)
        assert self.config.get_quick_cast_enabled() is True
    
    def test_set_quick_cast_hotkey(self):
        """Test setting quick-cast hotkeys."""
        self.config.set_quick_cast_hotkey("skill_1", "a")
        assert self.config.get_quick_cast_hotkeys()["skill_1"] == "a"
    
    def test_set_auto_cast_enabled(self):
        """Test setting auto-cast enabled state."""
        self.config.set_auto_cast_enabled(True)
        assert self.config.get_auto_cast_enabled() is True
        
        self.config.set_auto_cast_enabled(False)
        assert self.config.get_auto_cast_enabled() is False
    
    def test_add_auto_cast_skill(self):
        """Test adding auto-cast skills."""
        skill = {"hotkey": "q", "interval_ms": 200}
        self.config.add_auto_cast_skill(skill)
        
        skills = self.config.get_auto_cast_skills()
        assert len(skills) == 1
        assert skills[0]["hotkey"] == "q"
        assert skills[0]["interval_ms"] == 200
    
    def test_remove_auto_cast_skill(self):
        """Test removing auto-cast skills."""
        skill = {"hotkey": "q", "interval_ms": 200}
        self.config.add_auto_cast_skill(skill)
        
        assert self.config.remove_auto_cast_skill("q") is True
        assert len(self.config.get_auto_cast_skills()) == 0
        
        # Try to remove non-existent skill
        assert self.config.remove_auto_cast_skill("w") is False
    
    def test_add_macro(self):
        """Test adding custom macros."""
        macro = {
            "name": "test_macro",
            "hotkey": "x",
            "actions": [{"type": "key_press", "key": "q"}]
        }
        self.config.add_macro(macro)
        
        macros = self.config.get_macros()
        assert len(macros) == 1
        assert macros[0]["name"] == "test_macro"
    
    def test_remove_macro(self):
        """Test removing custom macros."""
        macro = {
            "name": "test_macro",
            "hotkey": "x",
            "actions": [{"type": "key_press", "key": "q"}]
        }
        self.config.add_macro(macro)
        
        assert self.config.remove_macro("test_macro") is True
        assert len(self.config.get_macros()) == 0
        
        # Try to remove non-existent macro
        assert self.config.remove_macro("nonexistent") is False
    
    def test_save_and_load(self):
        """Test saving and loading configuration."""
        self.config.set_quick_cast_enabled(False)
        self.config.set_auto_cast_enabled(True)
        self.config.add_auto_cast_skill({"hotkey": "q", "interval_ms": 150})
        
        # Save
        assert self.config.save() is True
        assert os.path.exists(self.config_path)
        
        # Create new config instance and load
        new_config = MacroConfig(self.config_path)
        assert new_config.load() is True
        
        assert new_config.get_quick_cast_enabled() is False
        assert new_config.get_auto_cast_enabled() is True
        assert len(new_config.get_auto_cast_skills()) == 1
    
    def test_global_hotkey(self):
        """Test global hotkey settings."""
        assert self.config.get_global_hotkey() == "f9"
        
        self.config.set_global_hotkey("f10")
        assert self.config.get_global_hotkey() == "f10"
    
    def test_load_nonexistent_file(self):
        """Test loading from a non-existent file."""
        config = MacroConfig("/nonexistent/path/config.yaml")
        assert config.load() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
