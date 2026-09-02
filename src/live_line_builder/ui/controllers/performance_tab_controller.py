from PySide6.QtWidgets import QFrame, QScrollArea, QWidget

from live_line_builder.ui.views import WorkSheetTabWidget


class PerformanceTabController:
    def __init__(self, view: WorkSheetTabWidget) -> None:
        self._view = view

    def set_tabs(self, tabs: list[tuple[str, QWidget, QWidget]]) -> None:
        """タブのタイトルとウィジェットのリストを受け取り、タブを設定する"""
        self._view.clear()  # 既存のタブをクリア
        for title, widget, graph_widget in tabs:
            scroll_area = QScrollArea()
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
            scroll_area.setWidgetResizable(True)
            # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
            scroll_area.setMinimumSize(250, 200)
            scroll_area.setWidget(widget)
            self._view.add_new_tab(scroll_area)
            index = self._view.indexOf(scroll_area)
            self._view.setTabText(index, title)
