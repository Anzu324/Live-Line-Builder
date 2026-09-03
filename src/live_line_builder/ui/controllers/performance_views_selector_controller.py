from PySide6.QtWidgets import QWidget

from live_line_builder.ui.views.combo_box_tabs_view import ComboBoxTabsView


class PerformanceViewSelectorController:
    def __init__(self, view: ComboBoxTabsView):
        self._view = view

    def set_performance_views(self, performance_views: list[QWidget]):
        self._view.clear_widgets()
        self._view.set_widgets(performance_views)
        # 4. リストの選択変更（currentRowChanged）をスタック画面の切り替え（setCurrentIndex）に接続
        self._view.combo_box.currentIndexChanged.connect(
            self._view.stacked_widget.setCurrentIndex
        )

        self._view.combo_box.setCurrentIndex(0)  # 最初のタブを選択状態にする
