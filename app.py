import sys

from PySide6.QtWidgets import QApplication
from rps.ui.window import MainWindow


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
