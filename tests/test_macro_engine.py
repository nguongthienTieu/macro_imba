"""Tests for the MacroEngine class."""
import os
import tempfile
import pytest
import time

from core.config import MacroConfig
from core.macro_engine import MacroEngine, PYNPUT_AVAILABLE


class TestMacroEngine:
    """Test cases for MacroEngine."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")
        self.config = MacroConfig(self.config_path)
        self.engine = MacroEngine(self.config)
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        self.engine.stop()
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initial_state(self):
        """Test engine initial state."""
        assert self.engine.running is False
        assert self.engine.enabled is False
    
    def test_quick_cast_settings(self):
        """Test quick-cast enable/disable."""
        self.engine.set_quick_cast_enabled(True)
        assert self.config.get_quick_cast_enabled() is True
        
        self.engine.set_quick_cast_enabled(False)
        assert self.config.get_quick_cast_enabled() is False
    
    def test_auto_cast_settings(self):
        """Test auto-cast enable/disable."""
        self.engine.set_auto_cast_enabled(True)
        assert self.config.get_auto_cast_enabled() is True
        
        self.engine.set_auto_cast_enabled(False)
        assert self.config.get_auto_cast_enabled() is False
    
    def test_add_auto_cast_skill(self):
        """Test adding auto-cast skill through engine."""
        self.engine.add_auto_cast_skill("q", 200)
        
        skills = self.config.get_auto_cast_skills()
        assert len(skills) == 1
        assert skills[0]["hotkey"] == "q"
        assert skills[0]["interval_ms"] == 200
    
    def test_remove_auto_cast_skill(self):
        """Test removing auto-cast skill through engine."""
        self.engine.add_auto_cast_skill("q", 200)
        assert self.engine.remove_auto_cast_skill("q") is True
        assert len(self.config.get_auto_cast_skills()) == 0
    
    def test_add_macro(self):
        """Test adding custom macro through engine."""
        actions = [
            {"type": "key_press", "key": "q"},
            {"type": "delay", "delay_ms": 50}
        ]
        self.engine.add_macro("test_macro", "x", actions)
        
        macros = self.config.get_macros()
        assert len(macros) == 1
        assert macros[0]["name"] == "test_macro"
        assert macros[0]["hotkey"] == "x"
    
    def test_remove_macro(self):
        """Test removing custom macro through engine."""
        actions = [{"type": "key_press", "key": "q"}]
        self.engine.add_macro("test_macro", "x", actions)
        
        assert self.engine.remove_macro("test_macro") is True
        assert len(self.config.get_macros()) == 0
    
    def test_save_settings(self):
        """Test saving settings through engine."""
        self.engine.add_auto_cast_skill("w", 300)
        assert self.engine.save_settings() is True
        assert os.path.exists(self.config_path)
    
    def test_reload_settings(self):
        """Test reloading settings."""
        # Modify config directly
        self.config.set_quick_cast_enabled(False)
        self.config.save()
        
        # Reload through engine
        self.engine.reload_settings()
        # Engine should have reloaded the setting
        assert self.config.get_quick_cast_enabled() is False
    
    @pytest.mark.skipif(not PYNPUT_AVAILABLE, reason="pynput not available")
    def test_start_stop(self):
        """Test starting and stopping the engine."""
        assert self.engine.start() is True
        assert self.engine.running is True
        assert self.engine.enabled is True
        
        self.engine.stop()
        assert self.engine.running is False
        assert self.engine.enabled is False
    
    @pytest.mark.skipif(not PYNPUT_AVAILABLE, reason="pynput not available")
    def test_toggle(self):
        """Test toggling the engine."""
        self.engine.start()
        
        # Toggle off
        result = self.engine.toggle()
        assert result is False
        assert self.engine.enabled is False
        
        # Toggle on
        result = self.engine.toggle()
        assert result is True
        assert self.engine.enabled is True
        
        self.engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
