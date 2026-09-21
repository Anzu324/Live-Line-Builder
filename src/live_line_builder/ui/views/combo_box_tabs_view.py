from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class ComboBoxTabsView(QWidget):
    def __init__(self, widgets: list[QWidget] | None = None, parent=None):
        super().__init__(parent=parent)
        v_layout = QVBoxLayout(self)

        self.combo_box = QComboBox(self)
        self.stacked_widget = QStackedWidget(self)

        v_layout.addWidget(self.combo_box)
        v_layout.addWidget(self.stacked_widget)

        # 1. 選択変更を画面切り替えに接続
        self.combo_box.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)

        # 初期化時にリストが渡されたら一括追加
        if widgets:
            self.set_widgets(widgets)

    def clear_widgets(self):
        """すべてのタブを削除"""
        self.combo_box.clear()
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            if widget is not None:
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()

    def set_widgets(self, widgets: list[QWidget]):
        """既存をクリアして一括再セット"""
        self.clear_widgets()
        for widget in widgets:
            self.add_widget(widget)

    def add_widget(self, widget: QWidget):
        """単一ウィジェットを追加（共通処理）"""
        title = self._try_get_tab_name_by_widget(widget)
        self.combo_box.addItem(title)

        scroll_area = QScrollArea()
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidgetResizable(True)

        # スクロールエリア自体が周囲のレイアウトで潰されないように設定
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 💡 【アップデート】
        # ウィジェットが親に配置され、レイアウトが完全に確定した段階で
        # 正しいサイズを計算させて最小サイズをロックする関数を作ります。
        def adjust_widget_size():
            # レイアウトが設定されている（Noneではない）場合のみ activate() を呼ぶ
            current_layout = widget.layout()
            if current_layout is not None:
                current_layout.activate()

            # 確定した理想サイズを最小サイズに適用
            widget.setMinimumSize(widget.sizeHint())

        # まず現在のサイズでセット
        adjust_widget_size()
        scroll_area.setWidget(widget)

        # 💡 将来的に GroundPlanView 側で画像が読み込まれて「サイズが変わったよ！」
        # という通知（カスタムシグナルなど）を受け取れるように、
        # 必要に応じてここにサイズ再計算のアタッチをしておくと便利です。
        # 例：if hasattr(widget, "size_changed_signal"): widget.size_changed_signal.connect(adjust_widget_size)

        self.stacked_widget.addWidget(scroll_area)


    def update_tab_title(self, index: int, new_title: str):
        """後から特定タブの表示名を変更したい場合に使用"""
        if 0 <= index < self.combo_box.count():
            self.combo_box.setItemText(index, new_title)

    @staticmethod
    def _try_get_tab_name_by_widget(
        widget: QWidget, default: str = "Unnamed Tab"
    ) -> str:
        return getattr(widget, "view_tab_name", default)
