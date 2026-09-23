from PySide6.QtCore import QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QLabel, QTableView, QVBoxLayout, QWidget


class AudioPatchView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        QLabel()
        self.v_layout = QVBoxLayout()


# パッチ画面用のテーブルを表示します。
class AudioPatchTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._model = None
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)

        # サイズ調整
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )  # 列の幅を内容に合わせて自動調整する
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # 名前列に限り幅を最大になるよう調整する
        self.setColumnWidth(1, 50)  # タイプ列の幅を50pxに固定する
        self.adjust_table_height()  # 全体の高さの最小値をスクロール値されないように設定

    def adjust_table_height(self):
        h = (
            self.horizontalHeader().height()
            + self.verticalHeader().length()
            + (self.frameWidth() * 2)
        )

        # スクロールバーが出ない最小サイズとして設定
        self.setMinimumHeight(h)

    def set_model_of_table(self, source_model: QAbstractItemModel):
        self._model = source_model
        self.setModel(source_model)
