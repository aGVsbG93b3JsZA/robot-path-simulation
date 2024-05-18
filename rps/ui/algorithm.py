"""
算法选择部分GUI
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QScrollArea,
)
from PySide6.QtCore import Signal, Slot

from .customs import TitleLabel
from ..config import DEFAULT_ALG
from ..utils import get_class_init, get_algs
from ..aco import *
from ..classical import *


class AlgWidget(QWidget):
    """
    算法选择部分主要部件
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.addWidget(TitleLabel("选择算法"))
        self.alg_combo = AlgComboBox(self)
        self.layout.addWidget(self.alg_combo)
        self.layout.addWidget(TitleLabel("参数设置"))
        self.params_area = AlgParamsScrollArea()
        self.layout.addWidget(self.params_area)
        self.setLayout(self.layout)

        # 选择算法后更新参数
        self.alg_combo.signal.connect(self.params_area.params_layout.init_params)

    def get_alg(self):
        return self.params_area.params_layout.get_alg()


class AlgComboBox(QComboBox):
    """
    算法选择下拉框
    """

    signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(get_algs())
        self.setCurrentText(DEFAULT_ALG)
        self.currentIndexChanged.connect(self.set_alg)

    def set_alg(self):
        alg = self.currentText()
        self.signal.emit(alg)


class AlgParamsScrollArea(QScrollArea):
    """
    算法参数滚动区域
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        widget = QWidget()
        self.params_layout = AlgParamsLayout(widget)
        self.setWidget(widget)
        self.setWidgetResizable(True)


class AlgParamsLayout(QVBoxLayout):
    """
    算法参数布局
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_params(DEFAULT_ALG)

    def get_alg(self):
        for i in range(self.count()):
            widget = self.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                key = self.itemAt(i - 1).widget().text()
                self.params[key] = eval(widget.text())
        return eval(self.alg)(**self.params)

    def clear(self):
        while self.count():
            item = self.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @Slot(str)
    def init_params(self, alg: str):
        self.clear()
        self.alg = alg
        self.params = get_class_init(eval(alg))
        for key, value in self.params.items():
            label = QLabel(key)
            self.addWidget(label)
            edit = QLineEdit(str(value))
            self.addWidget(edit)
