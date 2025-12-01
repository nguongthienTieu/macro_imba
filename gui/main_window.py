# Main GUI window for Dota Imba Macro Tool
import sys
from typing import Optional, List, Dict, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton, 
        QCheckBox, QSpinBox, QListWidget, QListWidgetItem, QMessageBox,
        QFormLayout, QFrame, QComboBox, QGridLayout, QDialog
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QKeyEvent
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from core import MacroConfig, MacroEngine


class HotkeyButton(QPushButton):
    """A button that captures keyboard input for hotkey assignment."""
    
    def __init__(self, slot_name: str, slot_type: str, parent=None):
        super().__init__(parent)
        self.slot_name = slot_name
        self.slot_type = slot_type  # 'skill' or 'item'
        self.hotkey = ""
        self.capturing = False
        self.setFocusPolicy(Qt.StrongFocus)
        self._update_display()
        self.setMinimumSize(60, 60)
        self.setStyleSheet(self._get_normal_style())
        
    def _get_normal_style(self) -> str:
        """Get normal button style."""
        return """
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #34495e;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
        """
    
    def _get_capturing_style(self) -> str:
        """Get capturing mode button style."""
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 2px solid #c0392b;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """
    
    def _update_display(self) -> None:
        """Update button display text."""
        if self.capturing:
            self.setText("Bấm phím\nbất kỳ...")
            self.setToolTip("Bấm phím bất kỳ để chọn hotkey\n(Bấm Backspace để xoá hotkey)")
            self.setStyleSheet(self._get_capturing_style())
        elif self.hotkey:
            self.setText(self.hotkey.upper())
            self.setToolTip(f"Hotkey: {self.hotkey}\nClick để thay đổi")
            self.setStyleSheet(self._get_normal_style())
        else:
            self.setText("---")
            self.setToolTip("Click để gán hotkey")
            self.setStyleSheet(self._get_normal_style())
    
    def set_hotkey(self, hotkey: str) -> None:
        """Set the hotkey value."""
        self.hotkey = hotkey
        self._update_display()
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse click to start capturing."""
        if event.button() == Qt.LeftButton:
            self.start_capturing()
        super().mousePressEvent(event)
    
    def start_capturing(self) -> None:
        """Start capturing keyboard input."""
        self.capturing = True
        self._update_display()
        self.setFocus()
    
    def stop_capturing(self) -> None:
        """Stop capturing keyboard input."""
        self.capturing = False
        self._update_display()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press for hotkey assignment."""
        if not self.capturing:
            super().keyPressEvent(event)
            return
        
        key = event.key()
        
        # Handle backspace to clear hotkey
        if key == Qt.Key_Backspace:
            self.hotkey = ""
            self.stop_capturing()
            # Emit signal to parent
            if self.parent() and hasattr(self.parent(), 'parent'):
                main_window = self._find_main_window()
                if main_window:
                    main_window._on_hotkey_cleared(self.slot_name, self.slot_type)
            return
        
        # Handle escape to cancel
        if key == Qt.Key_Escape:
            self.stop_capturing()
            return
        
        # Get key text
        key_text = event.text()
        if key_text and key_text.isprintable():
            self.hotkey = key_text.lower()
            self.stop_capturing()
            # Emit signal to parent
            main_window = self._find_main_window()
            if main_window:
                main_window._on_hotkey_changed(self.slot_name, self.slot_type, self.hotkey)
        else:
            # Handle special keys
            key_map = {
                Qt.Key_F1: 'f1', Qt.Key_F2: 'f2', Qt.Key_F3: 'f3', Qt.Key_F4: 'f4',
                Qt.Key_F5: 'f5', Qt.Key_F6: 'f6', Qt.Key_F7: 'f7', Qt.Key_F8: 'f8',
                Qt.Key_F9: 'f9', Qt.Key_F10: 'f10', Qt.Key_F11: 'f11', Qt.Key_F12: 'f12',
                Qt.Key_Space: 'space', Qt.Key_Tab: 'tab',
            }
            if key in key_map:
                self.hotkey = key_map[key]
                self.stop_capturing()
                main_window = self._find_main_window()
                if main_window:
                    main_window._on_hotkey_changed(self.slot_name, self.slot_type, self.hotkey)
    
    def _find_main_window(self):
        """Find the main window parent."""
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent() if hasattr(parent, 'parent') else None
        return None
    
    def focusOutEvent(self, event) -> None:
        """Handle focus out to stop capturing."""
        if self.capturing:
            self.stop_capturing()
        super().focusOutEvent(event)


class MainWindow(QMainWindow):
    """Main application window for Dota Imba Macro Tool."""
    
    def __init__(self):
        super().__init__()
        self.config = MacroConfig()
        self.config.load()
        self.engine = MacroEngine(self.config)
        
        self.skill_buttons: Dict[str, HotkeyButton] = {}
        self.item_buttons: Dict[str, HotkeyButton] = {}
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self) -> None:
        """Setup the main UI."""
        self.setWindowTitle("Dota Imba Macro Tool")
        self.setMinimumSize(500, 600)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Status bar at top
        self._create_status_bar(main_layout)
        
        # Tab widget for different settings
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_hotkey_tab()
        self._create_auto_cast_tab()
        self._create_macro_tab()
        self._create_settings_tab()
        
        # Bottom buttons
        self._create_bottom_buttons(main_layout)
        
    def _create_status_bar(self, layout: QVBoxLayout) -> None:
        """Create the status bar at the top."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.setMinimumWidth(100)
        self.toggle_btn.clicked.connect(self._toggle_engine)
        status_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(status_frame)
    
    def _create_hotkey_tab(self) -> None:
        """Create the visual hotkey configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Instructions
        instruction_label = QLabel(
            "🎮 Click vào ô để gán hotkey. Bấm Backspace để xoá hotkey."
        )
        instruction_label.setStyleSheet("font-size: 13px; color: #3498db; padding: 5px;")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Skills section (2x4 grid = 8 skills)
        skills_group = QGroupBox("⚡ Skills (2x4)")
        skills_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        skills_layout = QGridLayout(skills_group)
        skills_layout.setSpacing(10)
        
        skill_labels = [
            ("skill_1", "Q"), ("skill_2", "W"), ("skill_3", "E"), ("skill_4", "R"),
            ("skill_5", "D"), ("skill_6", "F"), ("skill_7", "T"), ("skill_8", "G")
        ]
        
        for i, (skill_key, label) in enumerate(skill_labels):
            row = i // 4
            col = i % 4
            
            # Container for label + button
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)
            
            # Skill label
            skill_label = QLabel(label)
            skill_label.setAlignment(Qt.AlignCenter)
            skill_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            container_layout.addWidget(skill_label)
            
            # Hotkey button
            btn = HotkeyButton(skill_key, "skill", self)
            self.skill_buttons[skill_key] = btn
            container_layout.addWidget(btn)
            
            skills_layout.addWidget(container, row, col)
        
        layout.addWidget(skills_group)
        
        # Items section (2x3 grid = 6 items)
        items_group = QGroupBox("🎒 Items (2x3)")
        items_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        items_layout = QGridLayout(items_group)
        items_layout.setSpacing(10)
        
        item_labels = [
            ("item_1", "Item 1"), ("item_2", "Item 2"), ("item_3", "Item 3"),
            ("item_4", "Item 4"), ("item_5", "Item 5"), ("item_6", "Item 6")
        ]
        
        for i, (item_key, label) in enumerate(item_labels):
            row = i // 3
            col = i % 3
            
            # Container for label + button
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)
            
            # Item label
            item_label = QLabel(label)
            item_label.setAlignment(Qt.AlignCenter)
            item_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            container_layout.addWidget(item_label)
            
            # Hotkey button
            btn = HotkeyButton(item_key, "item", self)
            self.item_buttons[item_key] = btn
            container_layout.addWidget(btn)
            
            items_layout.addWidget(container, row, col)
        
        layout.addWidget(items_group)
        
        # Enable checkboxes
        checkbox_layout = QHBoxLayout()
        
        self.quick_cast_enabled = QCheckBox("Enable Quick-Cast cho Skills")
        self.quick_cast_enabled.stateChanged.connect(self._on_quick_cast_toggle)
        checkbox_layout.addWidget(self.quick_cast_enabled)
        
        self.item_enabled = QCheckBox("Enable Quick-Cast cho Items")
        self.item_enabled.stateChanged.connect(self._on_item_toggle)
        checkbox_layout.addWidget(self.item_enabled)
        
        layout.addLayout(checkbox_layout)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎯 Hotkeys")
        
    def _create_auto_cast_tab(self) -> None:
        """Create the Auto-Cast settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Enable checkbox
        self.auto_cast_enabled = QCheckBox("Enable Auto-Cast")
        self.auto_cast_enabled.stateChanged.connect(self._on_auto_cast_toggle)
        layout.addWidget(self.auto_cast_enabled)
        
        # Description
        desc = QLabel(
            "Auto-Cast automatically presses skill hotkeys at specified intervals.\n"
            "Useful for skills that need to be spammed or cast repeatedly."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Auto-cast skill list
        list_group = QGroupBox("Auto-Cast Skills")
        list_layout = QVBoxLayout(list_group)
        
        self.auto_cast_list = QListWidget()
        list_layout.addWidget(self.auto_cast_list)
        
        # Add skill controls
        add_layout = QHBoxLayout()
        
        add_layout.addWidget(QLabel("Hotkey:"))
        self.auto_cast_hotkey = QLineEdit()
        self.auto_cast_hotkey.setMaxLength(1)
        self.auto_cast_hotkey.setMaximumWidth(50)
        add_layout.addWidget(self.auto_cast_hotkey)
        
        add_layout.addWidget(QLabel("Interval (ms):"))
        self.auto_cast_interval = QSpinBox()
        self.auto_cast_interval.setRange(50, 5000)
        self.auto_cast_interval.setValue(100)
        add_layout.addWidget(self.auto_cast_interval)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_auto_cast_skill)
        add_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_auto_cast_skill)
        add_layout.addWidget(remove_btn)
        
        list_layout.addLayout(add_layout)
        layout.addWidget(list_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔄 Auto-Cast")
        
    def _create_macro_tab(self) -> None:
        """Create the Custom Macro settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc = QLabel(
            "Create custom macros with multiple actions.\n"
            "Macros can include key presses, mouse clicks, and delays."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Macro list
        list_group = QGroupBox("Custom Macros")
        list_layout = QVBoxLayout(list_group)
        
        self.macro_list = QListWidget()
        list_layout.addWidget(self.macro_list)
        
        # Add macro controls
        add_layout = QGridLayout()
        
        add_layout.addWidget(QLabel("Name:"), 0, 0)
        self.macro_name = QLineEdit()
        add_layout.addWidget(self.macro_name, 0, 1)
        
        add_layout.addWidget(QLabel("Hotkey:"), 0, 2)
        self.macro_hotkey = QLineEdit()
        self.macro_hotkey.setMaxLength(1)
        self.macro_hotkey.setMaximumWidth(50)
        add_layout.addWidget(self.macro_hotkey, 0, 3)
        
        add_layout.addWidget(QLabel("Actions (comma-separated keys):"), 1, 0, 1, 2)
        self.macro_actions = QLineEdit()
        self.macro_actions.setPlaceholderText("e.g., q,w,e,r (keys to press in sequence)")
        add_layout.addWidget(self.macro_actions, 1, 2, 1, 2)
        
        btn_layout = QHBoxLayout()
        
        add_macro_btn = QPushButton("Add Macro")
        add_macro_btn.clicked.connect(self._add_macro)
        btn_layout.addWidget(add_macro_btn)
        
        remove_macro_btn = QPushButton("Remove Macro")
        remove_macro_btn.clicked.connect(self._remove_macro)
        btn_layout.addWidget(remove_macro_btn)
        
        add_layout.addLayout(btn_layout, 2, 0, 1, 4)
        
        list_layout.addLayout(add_layout)
        layout.addWidget(list_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📝 Macros")
        
    def _create_settings_tab(self) -> None:
        """Create the General Settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Global settings
        settings_group = QGroupBox("Global Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.global_hotkey = QLineEdit()
        self.global_hotkey.setPlaceholderText("f9")
        self.global_hotkey.setMaximumWidth(100)
        settings_layout.addRow("Toggle Hotkey:", self.global_hotkey)
        
        layout.addWidget(settings_group)
        
        # Info
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "Dota Imba Macro Tool\n\n"
            "Features:\n"
            "• Quick-Cast: Instantly cast skills at cursor position\n"
            "• Auto-Cast: Automatically repeat skill casts\n"
            "• Custom Macros: Create your own key sequences\n\n"
            "Press the toggle hotkey to enable/disable during game.\n"
            "All settings are saved automatically."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ Settings")
        
    def _create_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Create the bottom button bar."""
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        reload_btn = QPushButton("🔄 Reload Settings")
        reload_btn.clicked.connect(self._load_settings)
        button_layout.addWidget(reload_btn)
        
        button_layout.addStretch()
        
        quit_btn = QPushButton("❌ Quit")
        quit_btn.clicked.connect(self.close)
        button_layout.addWidget(quit_btn)
        
        layout.addLayout(button_layout)
    
    def _on_hotkey_changed(self, slot_name: str, slot_type: str, hotkey: str) -> None:
        """Handle hotkey change from HotkeyButton."""
        if slot_type == "skill":
            self.config.set_quick_cast_hotkey(slot_name, hotkey)
        elif slot_type == "item":
            self.config.set_item_hotkey(slot_name, hotkey)
    
    def _on_hotkey_cleared(self, slot_name: str, slot_type: str) -> None:
        """Handle hotkey cleared from HotkeyButton."""
        if slot_type == "skill":
            self.config.clear_quick_cast_hotkey(slot_name)
        elif slot_type == "item":
            self.config.clear_item_hotkey(slot_name)
        
    def _load_settings(self) -> None:
        """Load settings from config to UI."""
        self.config.load()
        
        # Quick-cast settings
        self.quick_cast_enabled.setChecked(self.config.get_quick_cast_enabled())
        hotkeys = self.config.get_quick_cast_hotkeys()
        for skill_key, btn in self.skill_buttons.items():
            btn.set_hotkey(hotkeys.get(skill_key, ""))
        
        # Item settings
        self.item_enabled.setChecked(self.config.get_item_enabled())
        item_hotkeys = self.config.get_item_hotkeys()
        for item_key, btn in self.item_buttons.items():
            btn.set_hotkey(item_hotkeys.get(item_key, ""))
        
        # Auto-cast settings
        self.auto_cast_enabled.setChecked(self.config.get_auto_cast_enabled())
        self.auto_cast_list.clear()
        for skill in self.config.get_auto_cast_skills():
            item_text = f"Key: {skill.get('hotkey', '')} - Interval: {skill.get('interval_ms', 100)}ms"
            self.auto_cast_list.addItem(item_text)
        
        # Macro settings
        self.macro_list.clear()
        for macro in self.config.get_macros():
            item_text = f"{macro.get('name', '')} [{macro.get('hotkey', '')}]"
            self.macro_list.addItem(item_text)
        
        # Global settings
        self.global_hotkey.setText(self.config.get_global_hotkey())
        
    def _save_settings(self) -> None:
        """Save settings from UI to config."""
        # Quick-cast settings
        self.config.set_quick_cast_enabled(self.quick_cast_enabled.isChecked())
        for skill_key, btn in self.skill_buttons.items():
            if btn.hotkey:
                self.config.set_quick_cast_hotkey(skill_key, btn.hotkey)
        
        # Item settings
        self.config.set_item_enabled(self.item_enabled.isChecked())
        for item_key, btn in self.item_buttons.items():
            if btn.hotkey:
                self.config.set_item_hotkey(item_key, btn.hotkey)
        
        # Global settings
        global_key = self.global_hotkey.text().strip()
        if global_key:
            self.config.set_global_hotkey(global_key)
        
        # Save to file
        if self.config.save():
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save settings.")
            
        # Reload engine settings
        self.engine.reload_settings()
        
    def _toggle_engine(self) -> None:
        """Toggle the macro engine on/off."""
        if self.engine.running:
            self.engine.stop()
            self.toggle_btn.setText("Start")
            self.status_label.setText("Status: Stopped")
        else:
            if self.engine.start():
                self.toggle_btn.setText("Stop")
                self.status_label.setText("Status: Running")
            else:
                QMessageBox.warning(
                    self, "Error", 
                    "Failed to start macro engine.\n"
                    "Make sure pynput is installed correctly."
                )
                
    def _on_quick_cast_toggle(self, state: int) -> None:
        """Handle quick-cast toggle."""
        enabled = state == Qt.Checked
        self.engine.set_quick_cast_enabled(enabled)
    
    def _on_item_toggle(self, state: int) -> None:
        """Handle item hotkeys toggle."""
        enabled = state == Qt.Checked
        self.config.set_item_enabled(enabled)
        
    def _on_auto_cast_toggle(self, state: int) -> None:
        """Handle auto-cast toggle."""
        enabled = state == Qt.Checked
        self.engine.set_auto_cast_enabled(enabled)
        
    def _add_auto_cast_skill(self) -> None:
        """Add a skill to auto-cast list."""
        hotkey = self.auto_cast_hotkey.text().strip()
        interval = self.auto_cast_interval.value()
        
        if not hotkey:
            QMessageBox.warning(self, "Error", "Please enter a hotkey.")
            return
        
        self.engine.add_auto_cast_skill(hotkey, interval)
        
        item_text = f"Key: {hotkey} - Interval: {interval}ms"
        self.auto_cast_list.addItem(item_text)
        
        self.auto_cast_hotkey.clear()
        
    def _remove_auto_cast_skill(self) -> None:
        """Remove selected skill from auto-cast list."""
        current = self.auto_cast_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Error", "Please select a skill to remove.")
            return
        
        # Extract hotkey from item text
        text = current.text()
        hotkey = text.split("Key: ")[1].split(" -")[0]
        
        if self.engine.remove_auto_cast_skill(hotkey):
            self.auto_cast_list.takeItem(self.auto_cast_list.row(current))
        
    def _add_macro(self) -> None:
        """Add a custom macro."""
        name = self.macro_name.text().strip()
        hotkey = self.macro_hotkey.text().strip()
        actions_str = self.macro_actions.text().strip()
        
        if not name or not hotkey or not actions_str:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        
        # Parse actions (simple key press sequence)
        keys = [k.strip() for k in actions_str.split(",") if k.strip()]
        actions = []
        for key in keys:
            actions.append({"type": "key_press", "key": key})
            actions.append({"type": "delay", "delay_ms": 50})
        
        self.engine.add_macro(name, hotkey, actions)
        
        item_text = f"{name} [{hotkey}]"
        self.macro_list.addItem(item_text)
        
        self.macro_name.clear()
        self.macro_hotkey.clear()
        self.macro_actions.clear()
        
    def _remove_macro(self) -> None:
        """Remove selected macro."""
        current = self.macro_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Error", "Please select a macro to remove.")
            return
        
        # Extract name from item text
        text = current.text()
        name = text.split(" [")[0]
        
        if self.engine.remove_macro(name):
            self.macro_list.takeItem(self.macro_list.row(current))
            
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.engine.stop()
        self.config.save()
        event.accept()


def run_app() -> int:
    """Run the main application."""
    if not PYQT_AVAILABLE:
        print("Error: PyQt5 is not installed. Please install it with: pip install PyQt5")
        return 1
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()
