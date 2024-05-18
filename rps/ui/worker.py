from PySide6.QtCore import QRunnable, Slot


class Runner(QRunnable):
    """
    算法线程类
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.start_signal = parent.start_signal
        self.finish_signal = parent.finish_signal

    def set_task(self, alg, real_time):
        self.alg = alg
        self.real_time = real_time
        self.stopped = 0

    def stop(self):
        self.stopped = 1

    @Slot()
    def run(self):
        self.start_signal.emit()
        if self.alg.CLASS == "A_STAR":
            self._run_astar()
        else:
            self._run_aco()
        self.finish_signal.emit(self.stopped)

    def _run_aco(self):
        for path in self.alg.search_real_time():
            if self.stopped:
                break
            if self.real_time:
                self.parent.ax.set_title(
                    f"{self.alg.__class__.__name__}"
                    + f"  Iteration: {self.alg.iter_cnt} "
                    f"  Length: {path.length:.2f}"
                )
                self.parent.draw_path(path)

    def _run_astar(self):
        for point in self.alg.search_real_time():
            if self.stopped:
                break
            if self.real_time:
                self.parent.draw_point(point)
