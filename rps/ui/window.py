"""
软件窗口
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QFileDialog,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Slot

from .algorithm import AlgWidget
from .run import RunWidget
from .result import ResultWidget
from .canvas import MainCanvas, ShowDetailCanvas
from .design import DesignWidget, MapWidget
from .menus import FileMenu, RunMenu, AlgMenu
from .customs import ErrorMessageBox


class MainWindow(QMainWindow):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPS")
        central_widget = QWidget()
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.alg_widget = AlgWidget(self)
        self.run_widget = RunWidget(self)
        self.result_widget = ResultWidget(self)
        self.map_widget = MapWidget(self)
        self.canvas = MainCanvas(self)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.run_widget)
        right_layout.addWidget(self.result_widget)
        mid_layout = QVBoxLayout()
        mid_layout.addWidget(self.map_widget)
        mid_layout.addWidget(self.canvas)
        layout.addWidget(self.alg_widget)
        layout.addLayout(mid_layout)
        layout.addLayout(right_layout)

        self.menu = self.menuBar()
        self.file_menu = FileMenu(self)
        self.alg_menu = AlgMenu(self)
        self.run_menu = RunMenu(self)
        self.menu.addMenu(self.file_menu)
        self.menu.addMenu(self.alg_menu)
        self.menu.addMenu(self.run_menu)

        self.detail_window = DetailDataWindow()
        self.detail_window.hide()
        self.design_window = DesignWindow()
        self.design_window.hide()

        # 选择算法后更新路径名称
        self.alg_widget.alg_combo.signal.connect(self.run_widget.line_name.set_name)
        # 按下运行按钮后运行算法
        self.run_widget.run_button.signal.connect(self.run_algorithm)
        # 按下停止按钮后停止算法
        self.run_widget.stop_button.signal.connect(self.stop_algorithm)
        # 算法开始后禁止运行按钮
        self.canvas.start_signal.connect(self.run_widget.run_button.forbid_run)
        # 算法结束后解禁运行按钮
        self.canvas.finish_signal.connect(self.run_widget.run_button.allow_run)
        # 算法结束后将结果添加到结果列表
        self.canvas.result_signal.connect(self.result_widget.receive_result)
        # 清除路径结果同时清除画布
        self.result_widget.clear_signal.connect(self.canvas.clear_path)
        # 点击详细数据按钮后显示详细数据
        self.result_widget.show_detail_signal.connect(self.show_detail)
        # 点击选择文件按钮后加载文件
        self.map_widget.select_signal.connect(self.quick_load_map)
        # 点击编辑地图按钮后将地图设置为编辑模式
        self.map_widget.edit_signal.connect(self.edit_map)
        # 点击新建地图按钮后显示新建地图窗口
        self.map_widget.new_signal.connect(self.create_map)
        # 点击保存地图按钮后保存地图
        self.map_widget.save_signal.connect(self.save_map)
        # 点击新建地图的确定按钮后将地图设置为编辑模式
        self.design_window.widget.signal.connect(self.edit_map)

        self.show()

    def quick_load_map(self, name):
        """加载地图"""
        self.canvas.load(name)

    def load_file(self):
        """加载文件"""
        file, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*npz)")
        if file:
            self.canvas.load(file=file)

    def set_alg(self, alg):
        """设置算法"""
        self.alg_widget.alg_combo.setCurrentText(alg)

    @Slot()
    def run_algorithm(self, real_time=None):
        """运行算法"""
        alg = self.alg_widget.get_alg()
        run_setting = self.run_widget.run_setting
        if real_time is not None:
            run_setting["real_time"] = real_time
        self.canvas.run_algorithm(alg, run_setting)

    @Slot()
    def stop_algorithm(self):
        """停止算法"""
        self.canvas.stop_algorithm()

    @Slot(dict)
    def show_detail(self, data):
        """显示详细数据"""
        self.detail_window.set_data(data)

    @Slot()
    def clear_results(self):
        """清除所有路径"""
        self.result_widget.clear_all_results()

    @Slot(str, int, int)
    def edit_map(self, file=None, width=None, length=None):
        """编辑地图"""
        if self.canvas.editing:
            ErrorMessageBox.show("Already editing")
            return
        self.alg_widget.hide()
        self.run_widget.hide()
        self.result_widget.hide()
        self.map_widget.edit()
        if file is None:
            self.canvas.edit(new=False)
        else:
            self.canvas.edit(new=True, file=file, width=width, length=length)

    @Slot()
    def create_map(self):
        """新建地图"""
        if self.canvas.editing:
            ErrorMessageBox.show("Already editing")
            return
        if self.design_window.isHidden():
            self.design_window.show()

    @Slot()
    def save_map(self):
        """保存地图"""
        self.canvas.save_edit()
        # self.map_widget.map_combo.flush()
        self.alg_widget.show()
        self.run_widget.show()
        self.result_widget.show()


class DetailDataWindow(QMainWindow):
    """
    运行详情窗口
    """

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("数据详情")
        main_widget = QWidget()
        self.layout = QHBoxLayout(main_widget)
        self.canvas = ShowDetailCanvas()
        self.layout.addWidget(self.canvas)
        self.setCentralWidget(main_widget)

    def set_data(self, data):
        self.canvas.show_detail(data)
        if self.isHidden():
            self.show()


class DesignWindow(QMainWindow):
    """
    新建地图窗口
    """

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("新建地图")
        self.widget = DesignWidget()
        self.setCentralWidget(self.widget)
        self.widget.signal.connect(self.hide)
