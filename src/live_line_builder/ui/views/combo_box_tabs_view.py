from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class ComboBoxTabsView(QWidget):
    def __init__(self, widgets: list[QWidget], parent=None):
        super().__init__(parent=parent)
        v_layout = QVBoxLayout(self)
        self.combo_box = QComboBox(self)
        self._widgets = None

        self.stacked_widget = QStackedWidget(self)
        # self.stacked_widget.setFrameShape(QFrame.Shape.NoFrame)
        for widget in widgets:
            scroll_area = QScrollArea()
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
            scroll_area.setWidgetResizable(True)
            # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
            scroll_area.setMinimumSize(250, 200)
            scroll_area.setWidget(widget)
            self.stacked_widget.addWidget(scroll_area)
        v_layout.addWidget(self.combo_box)
        v_layout.addWidget(self.stacked_widget)
        self.setLayout(v_layout)

    def clear_widgets(self):
        self.combo_box.clear()
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)  # 先頭のウィジェットを取得
            if widget is not None:
                self.stacked_widget.removeWidget(widget)  # スタックから取り除く
                widget.deleteLater()  # メモリから安全に破棄する

    def set_widgets(self, widgets: list[QWidget]):
        """
        新しいウィジェットを追加する。clear_widgetsは自動で呼ばれる。
        Signal/Slotの登録は、ウィジェットを追加する前に行うこと。追加後に行うと、Signal/Slotが正しく動作しない場合がある
        """
        self.clear_widgets()

        for widget in widgets:
            self.combo_box.addItem(self._try_get_tab_name_by_widget(widget))
            scroll_area = QScrollArea()
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
            scroll_area.setWidgetResizable(True)
            # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
            scroll_area.setMinimumSize(250, 200)
            scroll_area.setWidget(widget)
            self.stacked_widget.addWidget(scroll_area)

    def add_widget(self, widget: QWidget):
        self.combo_box.addItem(self._try_get_tab_name_by_widget(widget))
        scroll_area = QScrollArea()
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
        scroll_area.setWidgetResizable(True)
        # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
        scroll_area.setMinimumSize(250, 200)
        scroll_area.setWidget(widget)
        self.stacked_widget.addWidget(scroll_area)

    @staticmethod
    def _try_get_tab_name_by_widget(
        widget: QWidget, default: str = "Unnamed Tab"
    ) -> str:
        """
        ウィジェットからタブ名を取得する
        getattrを使って、ウィジェットに'view_tab_name'属性があるかどうかを確認し、存在する場合はその値を返す。存在しない場合はデフォルト値を返す
        """
        return getattr(widget, "view_tab_name", default)
