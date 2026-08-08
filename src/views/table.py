from PySide6.QtCore import QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QTableView, QVBoxLayout, QWidget


# テーブルビューを表示するためのクラス
# テーブルビューとは各回線情報を表示するために使用されるものです。
class EquipmentTableView(QWidget):
    def __init__(self, source_model: QAbstractItemModel, parent=None):
        super().__init__(parent)

        self.view = QTableView(self)  # QTableViewのインスタンスを作成
        self.view.setModel(source_model)
        self.view.resize(600, 500)
        self.view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.view.verticalHeader().setVisible(False)

        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )  # 列の幅を内容に合わせて自動調整する
        self.view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # 名前列に限り幅を最大になるよう調整する
        self.view.setColumnWidth(1, 50)  # タイプ列の幅を50pxに固定する

        # レイアウトの作成とテーブルの追加
        self.layout_a = QVBoxLayout()
        self.layout_a.addWidget(self.view)

        self.layout_a.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_a)
