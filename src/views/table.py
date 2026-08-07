from PySide6.QtWidgets import QHeaderView, QTableView, QVBoxLayout, QWidget


# テーブルビューを表示するためのクラス
# テーブルビューとは各回線情報を表示するために使用されるものです。
class ConnectionTableView(QWidget):
    def __init__(self, source_model):
        super().__init__()

        self.view = QTableView(self)  # QTableViewのインスタンスを作成
        self.view.setModel(source_model)
        self.view.resize(600, 500)
        self.view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.view.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # 名前列に限り幅を自動調整する
        self.view.setColumnWidth(1, 50)  # タイプ列の幅を50pxに固定する

        # レイアウトの作成とテーブルの追加
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
