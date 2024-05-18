"""
自定义Action
"""

from PySide6.QtWidgets import QWidgetAction, QFileDialog
from PySide6.QtCore import Signal
from rps.config import DEFAULT_MAP_PATH


class QickLoadMapAction(QWidgetAction):
    """加载地图"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.setText(name)
        self.triggered.connect(lambda: parent.quick_load_map(name))


class SetAlgAction(QWidgetAction):
    """选择算法"""

    def __init__(self, parent=None, alg=None):
        super().__init__(parent)
        self.setText(alg)
        self.triggered.connect(lambda: parent.set_alg(alg))


class LoadFileAction(QWidgetAction):
    """选择文件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("选择文件")
        self.triggered.connect(parent.load_file)


class QuickRunAction(QWidgetAction):
    """实时运行"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("快速运行")
        self.triggered.connect(lambda: parent.run_algorithm(False))


class RealTimeRunAction(QWidgetAction):
    """实时运行"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("实时运行")
        self.triggered.connect(lambda: parent.run_algorithm(True))
