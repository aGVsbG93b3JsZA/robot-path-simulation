"""
自定义控件
"""

from PySide6.QtWidgets import QLabel, QMessageBox
from PySide6.QtGui import QFont


class TitleLabel(QLabel):
    """
    标题标签
    """

    def __init__(self, text=None, parent=None):
        super().__init__(text=text, parent=parent)
        font = QFont("Arial", 15)
        font.setBold(True)
        self.setFont(font)


class ErrorMessageBox(QMessageBox):
    """
    错误消息框
    """

    def __init__(self, text=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("错误")
        self.setText(text)
        self.setIcon(QMessageBox.Critical)
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_()

    @staticmethod
    def show(text, parent=None):
        ErrorMessageBox(text, parent)
