# Main GUI window for Dota Imba Macro Tool
import sys
from typing import Optional, List, Dict, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton, 
        QCheckBox, QSpinBox, QListWidget, QListWidgetItem, QMessageBox,
        QFormLayout, QFrame, QComboBox, QGridLayout
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from core import MacroConfig, MacroEngine


class MainWindow(QMainWindow):
    """Main application window for Dota Imba Macro Tool."""
    
    def __init__(self):
        super().__init__()
        self.config = MacroConfig()
        self.config.load()
        self.engine = MacroEngine(self.config)
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self) -> None:
        """Setup the main UI."""
        self.setWindowTitle("Dota Imba Macro Tool")
        self.setMinimumSize(600, 500)
        
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
        self._create_quick_cast_tab()
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
        
    def _create_quick_cast_tab(self) -> None:
        """Create the Quick-Cast settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Enable checkbox
        self.quick_cast_enabled = QCheckBox("Enable Quick-Cast")
        self.quick_cast_enabled.stateChanged.connect(self._on_quick_cast_toggle)
        layout.addWidget(self.quick_cast_enabled)
        
        # Description
        desc = QLabel(
            "Quick-Cast allows you to cast skills instantly at your cursor position.\n"
            "When enabled, pressing a skill hotkey will immediately cast the skill."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Hotkey configuration
        hotkey_group = QGroupBox("Skill Hotkeys")
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.quick_cast_inputs: Dict[str, QLineEdit] = {}
        
        skill_labels = [
            ("skill_1", "Skill 1 (Q)"),
            ("skill_2", "Skill 2 (W)"),
            ("skill_3", "Skill 3 (E)"),
            ("skill_4", "Skill 4 (R)"),
            ("skill_5", "Skill 5 (D)"),
            ("skill_6", "Skill 6 (F)")
        ]
        
        for skill_key, label in skill_labels:
            input_field = QLineEdit()
            input_field.setMaxLength(1)
            input_field.setMaximumWidth(50)
            self.quick_cast_inputs[skill_key] = input_field
            hotkey_layout.addRow(label + ":", input_field)
        
        layout.addWidget(hotkey_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Quick-Cast")
        
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
        
        self.tab_widget.addTab(tab, "Auto-Cast")
        
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
        
        self.tab_widget.addTab(tab, "Macros")
        
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
        
        self.tab_widget.addTab(tab, "Settings")
        
    def _create_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Create the bottom button bar."""
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        reload_btn = QPushButton("Reload Settings")
        reload_btn.clicked.connect(self._load_settings)
        button_layout.addWidget(reload_btn)
        
        button_layout.addStretch()
        
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.close)
        button_layout.addWidget(quit_btn)
        
        layout.addLayout(button_layout)
        
    def _load_settings(self) -> None:
        """Load settings from config to UI."""
        self.config.load()
        
        # Quick-cast settings
        self.quick_cast_enabled.setChecked(self.config.get_quick_cast_enabled())
        hotkeys = self.config.get_quick_cast_hotkeys()
        for skill_key, input_field in self.quick_cast_inputs.items():
            input_field.setText(hotkeys.get(skill_key, ""))
        
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
        for skill_key, input_field in self.quick_cast_inputs.items():
            text = input_field.text().strip()
            if text:
                self.config.set_quick_cast_hotkey(skill_key, text)
        
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
