import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QTabWidget

class HotkeyButton(QPushButton):
    def __init__(self, parent=None):
        super(HotkeyButton, self).__init__("Set Hotkey", parent)
        self.hotkey = None
        self.clicked.connect(self.open_dialog)

    def open_dialog(self):
        dialog = HotkeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.hotkey = dialog.hotkey
            self.setText(self.hotkey)

class HotkeyDialog(QDialog):
    def __init__(self, parent=None):
        super(HotkeyDialog, self).__init__(parent)
        self.setWindowTitle("Choose Hotkey")
        self.hotkey = None
        self.label = QLabel("Bấm phím bất kỳ để chọn hotkey (nhấn backspace để xóa hotkey)")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            self.hotkey = None
            self.accept()
        else:
            self.hotkey = event.text()
            self.accept()

class MacroBuilder(QWidget):
    def __init__(self, parent=None):
        super(MacroBuilder, self).__init__(parent)
        layout = QVBoxLayout()
        # Add components for macro building here
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Dota Imba Macro Tool")
        self.setStyleSheet("background-color: #2E2E2E;")

        # Tabs
        self.tabs = QTabWidget()
        self.quick_actions_tab = QWidget()
        self.macro_builder_tab = MacroBuilder()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.quick_actions_tab, "Quick Actions")
        self.tabs.addTab(self.macro_builder_tab, "Macro Builder")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.setCentralWidget(self.tabs)

        # Emergency Stop Button
        self.stop_button = QPushButton("Emergency Stop")
        self.stop_button.clicked.connect(self.emergency_stop)

        # WAR3 HOTKEY Status Label
        self.status_label = QLabel("WAR3 HOTKEY: None")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        self.quick_actions_tab.setLayout(layout)

        # Hero Dropdown
        self.hero_dropdown = QComboBox()
        self.hero_dropdown.addItems(["Invoker", "Tinker", "Pudge", "Other Heroes..."])
        layout.addWidget(self.hero_dropdown)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())