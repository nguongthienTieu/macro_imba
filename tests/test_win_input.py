"""Tests for the Windows DirectInput module."""
import pytest

from core.win_input import (
    get_direct_input_controller,
    WINDOWS_AVAILABLE,
    DirectInputController,
    FallbackController
)


class TestDirectInputController:
    """Test cases for DirectInput controller."""
    
    def test_get_controller(self):
        """Test getting the appropriate controller."""
        controller = get_direct_input_controller()
        
        if WINDOWS_AVAILABLE:
            assert isinstance(controller, DirectInputController)
            assert controller.available is True
        else:
            assert isinstance(controller, FallbackController)
            assert controller.available is False
    
    def test_fallback_controller(self):
        """Test that fallback controller returns False for all operations."""
        controller = FallbackController()
        
        assert controller.available is False
        assert controller.press_key('a') is False
        assert controller.release_key('a') is False
        assert controller.tap_key('a') is False
        assert controller.click_mouse('left') is False
    
    @pytest.mark.skipif(not WINDOWS_AVAILABLE, reason="Windows not available")
    def test_direct_input_controller_available(self):
        """Test that DirectInput controller is available on Windows."""
        controller = DirectInputController()
        assert controller.available is True
    
    @pytest.mark.skipif(WINDOWS_AVAILABLE, reason="Only test on non-Windows")
    def test_direct_input_not_available_on_non_windows(self):
        """Test that DirectInput is not available on non-Windows."""
        controller = get_direct_input_controller()
        assert controller.available is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
