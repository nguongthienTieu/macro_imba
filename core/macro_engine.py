# Macro engine for quick-cast, auto-cast, and custom macros
import time
import threading
from typing import Dict, Any, Optional, Callable, List

try:
    from pynput import mouse, keyboard
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

from .config import MacroConfig
from .win_input import get_direct_input_controller, WINDOWS_AVAILABLE


class MacroEngine:
    """Main engine for macro execution."""
    
    def __init__(self, config: Optional[MacroConfig] = None):
        self.config = config or MacroConfig()
        self.running = False
        self.enabled = False
        
        # Initialize pynput controllers for normal input
        if PYNPUT_AVAILABLE:
            self.keyboard_controller = KeyboardController()
            self.mouse_controller = MouseController()
        else:
            self.keyboard_controller = None
            self.mouse_controller = None
        
        # Initialize DirectInput controller for game compatibility (War3)
        self.direct_input = get_direct_input_controller()
        self.use_direct_input = WINDOWS_AVAILABLE  # Use DirectInput on Windows
        
        self._quick_cast_enabled = False
        self._auto_cast_enabled = False
        self._auto_cast_thread: Optional[threading.Thread] = None
        self._stop_auto_cast = threading.Event()
        
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._registered_hotkeys: Dict[str, Callable] = {}
        self._macro_threads: Dict[str, threading.Thread] = {}
        
    def start(self) -> bool:
        """Start the macro engine."""
        if not PYNPUT_AVAILABLE:
            return False
            
        if self.running:
            return True
            
        self.running = True
        self.enabled = True
        self._load_settings()
        self._start_keyboard_listener()
        
        if self._auto_cast_enabled:
            self._start_auto_cast_thread()
            
        return True
    
    def stop(self) -> None:
        """Stop the macro engine."""
        self.running = False
        self.enabled = False
        self._stop_auto_cast_thread()
        self._stop_keyboard_listener()
        self._stop_all_macros()
    
    def toggle(self) -> bool:
        """Toggle the macro engine on/off."""
        if self.enabled:
            self.enabled = False
            self._stop_auto_cast_thread()
        else:
            self.enabled = True
            if self._auto_cast_enabled:
                self._start_auto_cast_thread()
        return self.enabled
    
    def _load_settings(self) -> None:
        """Load settings from config."""
        self.config.load()
        self._quick_cast_enabled = self.config.get_quick_cast_enabled()
        self._auto_cast_enabled = self.config.get_auto_cast_enabled()
    
    def _start_keyboard_listener(self) -> None:
        """Start listening for keyboard events."""
        if not PYNPUT_AVAILABLE:
            return
            
        def on_press(key):
            if not self.enabled:
                return
            self._handle_key_press(key)
        
        self._keyboard_listener = keyboard.Listener(on_press=on_press)
        self._keyboard_listener.start()
    
    def _stop_keyboard_listener(self) -> None:
        """Stop keyboard listener."""
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
    
    def _handle_key_press(self, key) -> None:
        """Handle a key press event."""
        try:
            key_char = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_char = str(key)
        
        # Check global toggle hotkey
        global_hotkey = self.config.get_global_hotkey()
        if self._key_matches(key, global_hotkey):
            self.toggle()
            return
        
        # Check quick-cast hotkeys
        if self._quick_cast_enabled:
            self._handle_quick_cast(key, key_char)
        
        # Check custom macro hotkeys
        self._handle_macro_hotkey(key_char)
    
    def _key_matches(self, key, hotkey: str) -> bool:
        """Check if a key matches a hotkey string."""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower() == hotkey.lower()
            else:
                key_name = str(key).replace('Key.', '').lower()
                return key_name == hotkey.lower()
        except AttributeError:
            return False
    
    def _handle_quick_cast(self, key, key_char: str) -> None:
        """Handle quick-cast for a key press."""
        hotkeys = self.config.get_quick_cast_hotkeys()
        
        for skill_name, hotkey in hotkeys.items():
            if key_char and key_char.lower() == hotkey.lower():
                self._execute_quick_cast(hotkey)
                break
    
    def _execute_quick_cast(self, hotkey: str) -> None:
        """Execute a quick-cast action - press key and click at cursor position."""
        # Use DirectInput for game compatibility (War3)
        if self.use_direct_input and self.direct_input.available:
            self.direct_input.click_mouse('left')
        elif self.mouse_controller:
            self.mouse_controller.click(Button.left)
    
    def _handle_macro_hotkey(self, key_char: str) -> None:
        """Handle custom macro hotkey."""
        macros = self.config.get_macros()
        
        for macro in macros:
            if key_char and key_char.lower() == macro.get("hotkey", "").lower():
                self._execute_macro(macro)
                break
    
    def _execute_macro(self, macro: Dict[str, Any]) -> None:
        """Execute a custom macro."""
        actions = macro.get("actions", [])
        macro_name = macro.get("name", "unnamed")
        
        # Run macro in a separate thread
        if macro_name in self._macro_threads:
            # Macro already running, skip
            return
        
        def run_macro():
            for action in actions:
                if not self.enabled:
                    break
                self._execute_action(action)
            self._macro_threads.pop(macro_name, None)
        
        thread = threading.Thread(target=run_macro, daemon=True)
        self._macro_threads[macro_name] = thread
        thread.start()
    
    def _execute_action(self, action: Dict[str, Any]) -> None:
        """Execute a single macro action."""
        action_type = action.get("type", "")
        
        if action_type == "key_press":
            key = action.get("key", "")
            if key:
                # Use DirectInput for game compatibility (War3)
                if self.use_direct_input and self.direct_input.available:
                    self.direct_input.tap_key(key)
                elif self.keyboard_controller:
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
        
        elif action_type == "key_hold":
            key = action.get("key", "")
            duration = action.get("duration_ms", 100) / 1000
            if key:
                if self.use_direct_input and self.direct_input.available:
                    self.direct_input.press_key(key)
                    time.sleep(duration)
                    self.direct_input.release_key(key)
                elif self.keyboard_controller:
                    self.keyboard_controller.press(key)
                    time.sleep(duration)
                    self.keyboard_controller.release(key)
        
        elif action_type == "mouse_click":
            button_name = action.get("button", "left")
            if self.use_direct_input and self.direct_input.available:
                self.direct_input.click_mouse(button_name)
            elif self.mouse_controller:
                button = Button.left if button_name == "left" else Button.right
                self.mouse_controller.click(button)
        
        elif action_type == "delay":
            delay_ms = action.get("delay_ms", 100)
            time.sleep(delay_ms / 1000)
        
        elif action_type == "combo":
            keys = action.get("keys", [])
            if self.use_direct_input and self.direct_input.available:
                for key in keys:
                    self.direct_input.press_key(key)
                for key in reversed(keys):
                    self.direct_input.release_key(key)
            elif self.keyboard_controller:
                for key in keys:
                    self.keyboard_controller.press(key)
                for key in reversed(keys):
                    self.keyboard_controller.release(key)
    
    def _start_auto_cast_thread(self) -> None:
        """Start the auto-cast thread."""
        if self._auto_cast_thread and self._auto_cast_thread.is_alive():
            return
        
        self._stop_auto_cast.clear()
        self._auto_cast_thread = threading.Thread(target=self._auto_cast_loop, daemon=True)
        self._auto_cast_thread.start()
    
    def _stop_auto_cast_thread(self) -> None:
        """Stop the auto-cast thread."""
        self._stop_auto_cast.set()
        if self._auto_cast_thread:
            self._auto_cast_thread.join(timeout=1)
            self._auto_cast_thread = None
    
    def _auto_cast_loop(self) -> None:
        """Main loop for auto-casting skills."""
        interval_ms = self.config.get_auto_cast_interval()
        
        while not self._stop_auto_cast.is_set() and self.enabled:
            skills = self.config.get_auto_cast_skills()
            
            for skill in skills:
                if self._stop_auto_cast.is_set() or not self.enabled:
                    break
                    
                hotkey = skill.get("hotkey", "")
                if hotkey:
                    # Use DirectInput for game compatibility (War3)
                    if self.use_direct_input and self.direct_input.available:
                        self.direct_input.tap_key(hotkey)
                    elif self.keyboard_controller:
                        self.keyboard_controller.press(hotkey)
                        self.keyboard_controller.release(hotkey)
                    
                    skill_interval = skill.get("interval_ms", interval_ms)
                    time.sleep(skill_interval / 1000)
            
            time.sleep(interval_ms / 1000)
    
    def _stop_all_macros(self) -> None:
        """Stop all running macros."""
        self._macro_threads.clear()
    
    # Public API methods for GUI integration
    
    def set_quick_cast_enabled(self, enabled: bool) -> None:
        """Enable or disable quick-cast."""
        self._quick_cast_enabled = enabled
        self.config.set_quick_cast_enabled(enabled)
    
    def set_auto_cast_enabled(self, enabled: bool) -> None:
        """Enable or disable auto-cast."""
        self._auto_cast_enabled = enabled
        self.config.set_auto_cast_enabled(enabled)
        
        if enabled and self.running and self.enabled:
            self._start_auto_cast_thread()
        else:
            self._stop_auto_cast_thread()
    
    def set_direct_input_enabled(self, enabled: bool) -> None:
        """Enable or disable DirectInput mode for War3 compatibility."""
        self.use_direct_input = enabled and WINDOWS_AVAILABLE
    
    def add_auto_cast_skill(self, hotkey: str, interval_ms: int = 100) -> None:
        """Add a skill to auto-cast."""
        skill = {
            "hotkey": hotkey,
            "interval_ms": interval_ms
        }
        self.config.add_auto_cast_skill(skill)
    
    def remove_auto_cast_skill(self, hotkey: str) -> bool:
        """Remove a skill from auto-cast."""
        return self.config.remove_auto_cast_skill(hotkey)
    
    def add_macro(self, name: str, hotkey: str, actions: List[Dict[str, Any]]) -> None:
        """Add a custom macro."""
        macro = {
            "name": name,
            "hotkey": hotkey,
            "actions": actions
        }
        self.config.add_macro(macro)
    
    def remove_macro(self, name: str) -> bool:
        """Remove a custom macro."""
        return self.config.remove_macro(name)
    
    def save_settings(self) -> bool:
        """Save current settings to config file."""
        return self.config.save()
    
    def reload_settings(self) -> None:
        """Reload settings from config file."""
        self._load_settings()
