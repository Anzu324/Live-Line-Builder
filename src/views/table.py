from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class TableView(QWidget):
    def __init__(self):
        super().__init__()

        # テーブルウィジェットの作成
        self.table = QTableWidget(self)
        self.table.setRowCount(5)  # 行数を設定
        self.table.setColumnCount(3)  # 列数を設定
        self.table.setHorizontalHeaderLabels(["NO", "INST", "PORT"])  # 列ヘッダーを設定

        # テーブルにデータを追加
        for row in range(5):
            for column in range(3):
                item = QTableWidgetItem(f"Item {row + 1}, {column + 1}")
                self.table.setItem(row, column, item)

        # レイアウトの作成とテーブルの追加
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
