# Windows DirectInput support for Warcraft 3 and other games
# Uses ctypes to send low-level input that DirectX games can receive
import sys
import time
from typing import Optional

# Check if we're on Windows
WINDOWS_AVAILABLE = sys.platform == 'win32'

if WINDOWS_AVAILABLE:
    import ctypes
    from ctypes import wintypes
    
    # Windows API constants
    INPUT_KEYBOARD = 1
    INPUT_MOUSE = 0
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_EXTENDEDKEY = 0x0001
    
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    
    # Structures for SendInput
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
        ]
    
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
        ]
    
    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
        ]
    
    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("union", INPUT_UNION)
        ]
    
    # Virtual key codes to scan codes mapping for common keys
    VK_TO_SCANCODE = {
        # Letters (A-Z)
        'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12,
        'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
        'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
        'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14,
        'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15,
        'z': 0x2C,
        # Numbers (0-9)
        '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
        '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
        # Function keys
        'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
        'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
        'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
        # Special keys
        'space': 0x39, 'enter': 0x1C, 'escape': 0x01, 'esc': 0x01,
        'tab': 0x0F, 'backspace': 0x0E, 'shift': 0x2A, 'ctrl': 0x1D,
        'alt': 0x38, 'capslock': 0x3A,
        # Numpad
        'numpad0': 0x52, 'numpad1': 0x4F, 'numpad2': 0x50, 'numpad3': 0x51,
        'numpad4': 0x4B, 'numpad5': 0x4C, 'numpad6': 0x4D, 'numpad7': 0x47,
        'numpad8': 0x48, 'numpad9': 0x49,
    }
    
    # Virtual key codes
    VK_CODES = {
        # Letters (A-Z)
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
        'z': 0x5A,
        # Numbers (0-9)
        '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
        '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
        # Function keys
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
        'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
        'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
        # Special keys
        'space': 0x20, 'enter': 0x0D, 'escape': 0x1B, 'esc': 0x1B,
        'tab': 0x09, 'backspace': 0x08, 'shift': 0x10, 'ctrl': 0x11,
        'alt': 0x12, 'capslock': 0x14,
        # Numpad
        'numpad0': 0x60, 'numpad1': 0x61, 'numpad2': 0x62, 'numpad3': 0x63,
        'numpad4': 0x64, 'numpad5': 0x65, 'numpad6': 0x66, 'numpad7': 0x67,
        'numpad8': 0x68, 'numpad9': 0x69,
    }


class DirectInputController:
    """
    Controller that sends keyboard and mouse input using Windows DirectInput.
    This is compatible with DirectX games like Warcraft 3.
    """
    
    def __init__(self):
        self.available = WINDOWS_AVAILABLE
        
    def press_key(self, key: str) -> bool:
        """Press a key down."""
        if not self.available:
            return False
        
        key = key.lower()
        scancode = VK_TO_SCANCODE.get(key)
        vk = VK_CODES.get(key)
        
        if scancode is None:
            # If not in mapping, try single character
            if len(key) == 1:
                vk = ord(key.upper())
                scancode = ctypes.windll.user32.MapVirtualKeyW(vk, 0)
            else:
                return False
        
        # Create input structure with scancode (works better with games)
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = vk if vk else 0
        inp.union.ki.wScan = scancode
        inp.union.ki.dwFlags = KEYEVENTF_SCANCODE
        inp.union.ki.time = 0
        inp.union.ki.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
        
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        return True
    
    def release_key(self, key: str) -> bool:
        """Release a key."""
        if not self.available:
            return False
        
        key = key.lower()
        scancode = VK_TO_SCANCODE.get(key)
        vk = VK_CODES.get(key)
        
        if scancode is None:
            if len(key) == 1:
                vk = ord(key.upper())
                scancode = ctypes.windll.user32.MapVirtualKeyW(vk, 0)
            else:
                return False
        
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = vk if vk else 0
        inp.union.ki.wScan = scancode
        inp.union.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
        inp.union.ki.time = 0
        inp.union.ki.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
        
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        return True
    
    def tap_key(self, key: str, duration: float = 0.01) -> bool:
        """Press and release a key."""
        if not self.press_key(key):
            return False
        time.sleep(duration)
        return self.release_key(key)
    
    def click_mouse(self, button: str = 'left') -> bool:
        """Click a mouse button."""
        if not self.available:
            return False
        
        if button == 'left':
            down_flag = MOUSEEVENTF_LEFTDOWN
            up_flag = MOUSEEVENTF_LEFTUP
        elif button == 'right':
            down_flag = MOUSEEVENTF_RIGHTDOWN
            up_flag = MOUSEEVENTF_RIGHTUP
        elif button == 'middle':
            down_flag = MOUSEEVENTF_MIDDLEDOWN
            up_flag = MOUSEEVENTF_MIDDLEUP
        else:
            return False
        
        # Mouse down
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = 0
        inp.union.mi.dy = 0
        inp.union.mi.mouseData = 0
        inp.union.mi.dwFlags = down_flag
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        
        time.sleep(0.01)
        
        # Mouse up
        inp.union.mi.dwFlags = up_flag
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        
        return True


# Fallback controller for non-Windows systems
class FallbackController:
    """Fallback controller that does nothing (for non-Windows systems)."""
    
    def __init__(self):
        self.available = False
    
    def press_key(self, key: str) -> bool:
        return False
    
    def release_key(self, key: str) -> bool:
        return False
    
    def tap_key(self, key: str, duration: float = 0.01) -> bool:
        return False
    
    def click_mouse(self, button: str = 'left') -> bool:
        return False


def get_direct_input_controller():
    """Get the appropriate DirectInput controller for the current platform."""
    if WINDOWS_AVAILABLE:
        return DirectInputController()
    return FallbackController()
