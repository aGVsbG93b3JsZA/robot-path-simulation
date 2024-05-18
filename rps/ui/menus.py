"""
软件菜单
"""

from PySide6.QtWidgets import QMenu
from .actions import (
    QuickRunAction,
    RealTimeRunAction,
    QickLoadMapAction,
    LoadFileAction,
    SetAlgAction,
)
from ..utils import get_files, get_algs


class FileMenu(QMenu):
    """文件菜单"""

    def __init__(self, parent=None):
        super().__init__("文件", parent)
        self.addAction(LoadFileAction(parent))
        self.addSeparator()
        for file in get_files():
            self.addAction(QickLoadMapAction(parent, file))


class AlgMenu(QMenu):
    """算法菜单"""

    def __init__(self, parent=None):
        super().__init__("算法", parent)
        for alg in get_algs():
            self.addAction(SetAlgAction(parent, alg))


class RunMenu(QMenu):
    """运行菜单"""

    def __init__(self, parent=None):
        super().__init__("运行", parent)
        self.addAction(QuickRunAction(parent))
        self.addAction(RealTimeRunAction(parent))
