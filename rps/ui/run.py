"""
运行部分GUI
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QColorDialog,
    QButtonGroup,
    QRadioButton,
)

from PySide6.QtCore import Signal, Slot

from .customs import TitleLabel


class RunWidget(QWidget):
    """
    运行设置部分主要部件
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.addWidget(TitleLabel("运行设置"))
        self.layout.addWidget(QLabel("路径名称"))
        self.line_name = NameLineEdit()
        self.layout.addWidget(self.line_name)
        self.layout.addWidget(QLabel("路径颜色"))
        self.line_color = ColorButton()
        self.layout.addWidget(self.line_color)
        self.layout.addWidget(QLabel("路径样式"))
        self.line_style = StyleComboBox()
        self.layout.addWidget(self.line_style)
        self.layout.addWidget(TitleLabel("运行模式"))
        self.mode_group = ModeButtonGroup()
        self.layout.addWidget(self.mode_group.button1)
        self.layout.addWidget(self.mode_group.button2)
        self.run_button = RunButton()
        self.layout.addWidget(self.run_button)
        self.stop_button = StopButton()
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

    @property
    def run_setting(self):
        return {
            "name": self.line_name.line_name,
            "color": self.line_color.color,
            "style": self.line_style.line_style,
            "real_time": self.mode_group.real_time,
        }


class NameLineEdit(QLineEdit):
    """
    路径名称输入框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_name = ""
        self.textChanged.connect(self.update_name)

    @Slot(str)
    def set_name(self, str):
        self.setText(str)

    def update_name(self):
        self.line_name = self.text()


class ColorButton(QPushButton):
    """
    路径颜色选择按钮
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = "#00ffff"
        self.setStyleSheet(f"background-color: {self.color};")
        self.clicked.connect(self.pick_color)

    def pick_color(self):
        color_dialog = QColorDialog(self)
        color = color_dialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.setStyleSheet(f"background-color: {self.color}")


class StyleComboBox(QComboBox):
    """
    路径样式选择下拉框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_style = "-"
        self.addItems(["-", "--", "-.", ":"])
        self.currentIndexChanged.connect(self.set_style)

    def set_style(self):
        self.line_style = self.currentText()


class ModeButtonGroup(QButtonGroup):
    """
    运行模式选择按钮组
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.real_time = True
        self.button1 = QRadioButton("实时运行")
        self.button2 = QRadioButton("快速运行")
        self.button1.setChecked(True)
        self.addButton(self.button1, id=1)
        self.addButton(self.button2, id=0)
        self.buttonClicked.connect(self.on_button_clicked)

    def on_button_clicked(self, button):
        self.real_time = button == self.button1


class RunButton(QPushButton):
    """
    运行按钮
    """

    signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("运行")
        self.clicked.connect(self.signal.emit)

    @Slot()
    def allow_run(self, *args):
        self.setEnabled(True)

    @Slot()
    def forbid_run(self):
        self.setEnabled(False)


class StopButton(QPushButton):
    """
    停止按钮
    """

    signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("停止")
        self.clicked.connect(self.signal.emit)
