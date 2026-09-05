from PySide6.QtWidgets import QWidget

from live_line_builder.ui.controllers.performance_views_selector_controller import (
    PerformanceViewSelectorController,
)
from live_line_builder.ui.views import ComboBoxTabsView, WorkSheetTabWidget


class PerformanceTabController:
    def __init__(self, view: WorkSheetTabWidget) -> None:
        self._view = view

    def set_tabs(self, tabs: list[tuple[str, QWidget, QWidget]]) -> None:
        """タブのタイトルとウィジェットのリストを受け取り、タブを設定する"""
        self._view.clear()  # 既存のタブをクリア
        for title, widget, graph_widget in tabs:
            combo_box_tab = ComboBoxTabsView(parent=self._view)
            PerformanceViewSelectorController(combo_box_tab).set_performance_views(
                [widget, graph_widget]
            )
            self._view.add_new_tab(combo_box_tab)
            index = self._view.indexOf(combo_box_tab)
            self._view.setTabText(index, title)
