"""包含地图管理部件和新建地图窗口"""

import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QComboBox,
    QSpinBox,
)
from PySide6.QtCore import Qt, Signal, Slot
from rps.config import DEFAULT_MAP_PATH, DEFAULT_MAP_SAVE_PATH, DEFAULT_MAP_NAME

from rps.utils.common import get_files
from .customs import TitleLabel, ErrorMessageBox


class MapWidget(QWidget):
    """
    地图管理部件
    """

    edit_signal = Signal()
    new_signal = Signal()
    select_signal = Signal(str)
    save_signal = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.map_combo = MapComboBox(self)
        self.button_new = QPushButton("新建")
        self.button_edit = QPushButton("编辑")
        self.button_save = QPushButton("保存")
        self.layout.addWidget(self.map_combo)
        self.layout.addWidget(self.button_new)
        self.layout.addWidget(self.button_edit)
        self.layout.addWidget(self.button_save)
        self.button_new.clicked.connect(self.new_signal.emit)
        self.button_edit.clicked.connect(self.edit_signal.emit)
        self.button_save.clicked.connect(self.save_signal.emit)
        self.setLayout(self.layout)
        self.not_edit()
        self.button_save.clicked.connect(self.not_edit)
        self.button_save.clicked.connect(self.map_combo.flush)

    def edit(self):
        self.button_new.setEnabled(False)
        self.button_edit.setEnabled(False)
        self.button_save.setEnabled(True)
        self.map_combo.hide()

    def not_edit(self):
        self.button_new.setEnabled(True)
        self.button_edit.setEnabled(True)
        self.button_save.setEnabled(False)
        self.map_combo.show()


class MapComboBox(QComboBox):
    """
    地图选择下拉框
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.flush()
        self.setPlaceholderText("选择地图")
        self.activated.connect(self.select_map)

    def select_map(self, index):
        self.parent.select_signal.emit(self.currentText())

    @Slot()
    def flush(self):
        self.clear()
        for f in get_files():
            self.addItem(f)


class DesignWidget(QWidget):
    """
    新建地图窗口
    """

    signal = Signal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.addWidget(TitleLabel("地图名称"))
        self.map_name = QLineEdit()
        self.layout.addWidget(self.map_name)
        self.layout.addWidget(TitleLabel("地图大小"))
        self.layout_size = QHBoxLayout()
        self.layout_size.addWidget(QLabel("宽度"))
        self.map_width = QSpinBox()
        self.map_width.setRange(5, 50)
        self.map_width.setValue(20)
        self.layout_size.addWidget(self.map_width)
        self.layout_size.addWidget(QLabel("长度"))
        self.map_length = QSpinBox()
        self.map_length.setRange(5, 50)
        self.map_length.setValue(20)
        self.layout_size.addWidget(self.map_length)
        self.layout.addLayout(self.layout_size)
        self.layout.addWidget(TitleLabel("保存路径"))
        self.map_path = QLineEdit(os.path.join(os.getcwd(), DEFAULT_MAP_SAVE_PATH))
        self.layout.addWidget(self.map_path)
        self.button_path = QPushButton("更换路径")
        self.button_path.clicked.connect(self.select_path)
        self.button_confirm = QPushButton("确定")
        self.button_confirm.clicked.connect(self.confirm)
        self.layout.addWidget(self.button_path)
        self.layout.addWidget(self.button_confirm)
        self.setLayout(self.layout)

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", DEFAULT_MAP_PATH)
        if path:
            self.map_path.setText(path)

    def confirm(self):
        path = self.map_path.text()
        try:
            exists = get_files(path)
        except FileNotFoundError:
            ErrorMessageBox.show("Invalid path")
            return
        name = self.map_name.text()
        if name in exists:
            ErrorMessageBox.show("Name already exists")
            return
        if name == "":
            ErrorMessageBox.show("Name cannot be empty")
            return
        file = os.path.join(path, name)
        width = self.map_width.value()
        length = self.map_length.value()
        self.signal.emit(file, width, length)
