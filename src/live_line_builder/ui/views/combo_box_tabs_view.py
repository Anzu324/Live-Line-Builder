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
        self.combo_box.addItems(["Plan Sheet", "Patch Graph"])
        self._widgets = widgets

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
