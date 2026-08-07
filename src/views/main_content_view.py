from PySide6.QtWidgets import QHBoxLayout, QWidget

from views.table import ConnectionTableView  # テーブルビューをインポート


class MainContentView(QWidget):
    def __init__(self, source_model):
        super().__init__()

        self.h_layout = QHBoxLayout(self)  # 垂直方向のレイアウトを作成

        self.table1_view = ConnectionTableView(
            source_model
        )  # QTableViewのインスタンスを作成

        self.table2_view = ConnectionTableView(
            source_model
        )  # QTableViewのインスタンスを作成

        self.table3_view = ConnectionTableView(
            source_model
        )  # QTableViewのインスタンスを作成

        self.h_layout.addWidget(self.table1_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table2_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table3_view)  # レイアウトにQTableViewを追加
        self.setLayout(self.h_layout)  # 垂直レイアウトに水平レイアウトを追
