from PySide6.QtCore import QRegularExpression, QSortFilterProxyModel
from PySide6.QtWidgets import QHBoxLayout, QWidget

from views.table import EquipmentTableView  # テーブルビューをインポート


class MainContentView(QWidget):
    def __init__(self, source_model, parent=None):
        super().__init__(parent)

        self.h_layout = QHBoxLayout(self)  # 垂直方向のレイアウトを作成

        proxy_model = QSortFilterProxyModel()

        proxy_model.setSourceModel(source_model)  # 元のModelをセット

        # ★ 1. 検索対象の「列番号（0始まり）」を指定する（例: 2列目を対象にする）
        proxy_model.setFilterKeyColumn(1)

        # ★ 2. 完全一致させたい検索値（例: "完了"）
        target_value = "Mixer"

        # 正規表現で「先頭(^)から末尾($)まで完全一致」というパターンを作る
        pattern = f"^{QRegularExpression.escape(target_value)}$"
        regex = QRegularExpression(
            pattern, QRegularExpression.PatternOption.CaseInsensitiveOption
        )

        # フィルターをセット
        proxy_model.setFilterRegularExpression(regex)
        self.table1_view = EquipmentTableView(
            source_model
        )  # QTableViewのインスタンスを作成

        self.table2_view = EquipmentTableView(
            proxy_model
        )  # QTableViewのインスタンスを作成

        self.table3_view = EquipmentTableView(
            source_model
        )  # QTableViewのインスタンスを作成

        self.h_layout.addWidget(self.table1_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table2_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table3_view)  # レイアウトにQTableViewを追加
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(10)  # レイアウトの余白を10に設定

        self.setLayout(self.h_layout)  # 垂直レイアウトに水平レイアウトを追
