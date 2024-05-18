"""
运行结果显示部件
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QWidget,
)
from PySide6.QtCore import Signal, Slot
from .customs import TitleLabel


class ResultWidget(QWidget):
    """
    结果设置部分主要部件
    """

    clear_signal = Signal(str)
    show_detail_signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.selected = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(TitleLabel("运行结果"))
        self.result_combo = ResultComboBox()
        self.layout.addWidget(self.result_combo)
        self.length_label = QLabel("路径长度:")
        self.layout.addWidget(self.length_label)
        self.turn_num_label = QLabel("转向次数:")
        self.layout.addWidget(self.turn_num_label)

        self.detail_button = QPushButton("查看运行详情")
        self.layout.addWidget(self.detail_button)
        self.clear_button = QPushButton("清除当前路径")
        self.layout.addWidget(self.clear_button)
        self.clear_all_button = QPushButton("清除所有路径")
        self.layout.addWidget(self.clear_all_button)

        self.result_combo.signal.connect(self.select_result)
        self.clear_button.clicked.connect(self.clear_result)
        self.clear_all_button.clicked.connect(self.clear_all_results)
        self.detail_button.clicked.connect(
            lambda: self.show_detail_signal.emit(self.data)
        )

    @Slot(str, dict)
    def receive_result(self, name, data):
        self.data[name] = data
        self.result_combo.addItem(name)
        self.result_combo.setCurrentText(name)
        self.length_label.setText(f"路径长度: {data['length']: .2f}")
        self.turn_num_label.setText(f"转向次数: {data['turn_num']}")

    def clear_result(self):
        name = self.result_combo.currentText()
        if name == "":
            return
        self.clear_signal.emit(name)
        self.data.pop(name)
        self.result_combo.removeItem(self.result_combo.currentIndex())

    def clear_all_results(self):
        self.clear_signal.emit("all")
        self.data.clear()
        self.result_combo.clear()
        self.length_label.setText("路径长度:")
        self.turn_num_label.setText("转向次数:")

    def select_result(self):
        name = self.result_combo.currentText()
        if name == "":
            return
        self.selected = name
        data = self.data[name]
        self.length_label.setText(f"路径长度: {data['length']: .2f}")
        self.turn_num_label.setText(f"转向次数: {data['turn_num']}")


class ResultComboBox(QComboBox):
    """
    算法结果选择框
    """

    signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentTextChanged.connect(self.on_current_text_changed)

    def on_current_text_changed(self, text):
        self.signal.emit(text)
