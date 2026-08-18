from PySide6.QtCore import QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QLabel, QTableView, QVBoxLayout, QWidget


# テーブルビューを表示するためのクラス
# テーブルビューとは各回線情報を表示するために使用されるものです。
class EquipmentTableView(QWidget):
    def __init__(self, title: str, source_model: QAbstractItemModel, parent=None):
        super().__init__(parent)

        title_label = QLabel(title)  # タイトルラベルを作成

        self._model = source_model

        self.table = QTableView(self)  # QTableViewのインスタンスを作成
        self.table.setModel(source_model)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # サイズ調整
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )  # 列の幅を内容に合わせて自動調整する
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # 名前列に限り幅を最大になるよう調整する
        self.table.setColumnWidth(1, 50)  # タイプ列の幅を50pxに固定する
        self.adjust_table_height()  # 全体の高さの最小値をスクロール値されないように設定

        # レイアウトの作成とテーブルの追加
        self.layout_a = QVBoxLayout()
        self.layout_a.addWidget(title_label)
        self.layout_a.addWidget(self.table)

        self.layout_a.setContentsMargins(0, 0, 0, 0)
        self.layout_a.setSpacing(1)
        self.setLayout(self.layout_a)

    def adjust_table_height(self):
        h = (
            self.table.horizontalHeader().height()
            + self.table.verticalHeader().length()
            + (self.table.frameWidth() * 2)
        )

        # スクロールバーが出ない最小サイズとして設定
        self.table.setMinimumHeight(h)

    def set_model_of_table(self, source_model: QAbstractItemModel):
        self._model = source_model
        self.table.setModel(source_model)
