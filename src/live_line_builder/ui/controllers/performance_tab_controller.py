from PySide6.QtWidgets import QWidget

from live_line_builder.ui.controllers.performance_views_selector_controller import (
    PerformanceViewSelectorController,
)
from live_line_builder.ui.models import PerformanceGroupModel
from live_line_builder.ui.views import ComboBoxTabsView, WorkSheetTabWidget


class PerformanceTabController:
    def __init__(
        self, view: WorkSheetTabWidget, performance_group: PerformanceGroupModel
    ) -> None:
        self._view = view
        self.group_model = performance_group

    def set_tabs(self, tabs: list[tuple[str, QWidget, QWidget]]) -> None:
        """タブのタイトルとウィジェットのリストを受け取り、タブを設定する"""
        self._view.clear()  # 既存のタブをクリア
        models = self.group_model.get_performace_info_models()

        for index, (title, widget, graph_widget) in enumerate(tabs):
            if index >= len(models):
                break

            combo_box_tab = ComboBoxTabsView(parent=self._view)
            PerformanceViewSelectorController(
                combo_box_tab, models[index]
            ).set_performance_views([widget, graph_widget])
            self._view.add_new_tab(combo_box_tab)
            tab_index = self._view.indexOf(combo_box_tab)
            self._view.setTabText(tab_index, title)
