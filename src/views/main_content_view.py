from PySide6.QtCore import QAbstractItemModel, QSortFilterProxyModel
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from models.proxies.multi_filter_proxy import (
    ExactMatchProxyModel,  # プロキシモデルをインポート
)
from views.table import EquipmentTableView  # テーブルビューをインポート


class MainContentView(QWidget):
    def __init__(
        self,
        equipment_model: QAbstractItemModel,
        connector_model: QAbstractItemModel,
        multi_id_list: list[int],
        parent=None,
    ):
        super().__init__(parent)

        self.h_layout = QHBoxLayout(self)  # 垂直方向のレイアウトを作成

        self.multi_column_layout = QVBoxLayout()  # マルチの列のレイアウトを作成
        self.multi_column_layout.setContentsMargins(0, 0, 0, 0)
        self.multi_column_layout.setSpacing(1)  # レイアウトの余白を1に設定
        self.multi_table_views = []  # マルチの列のテーブルビューを保持するリスト

        for x in multi_id_list:
            print(f"Creating table for equipment ID: {x}")  # デバッグ用の出力
            proxy_model = ExactMatchProxyModel()
            proxy_model.setSourceModel(connector_model)  # 元のModelをセット
            proxy_model.set_filter_condition(0, str(x))  # フィルター対象の列と値を指定

            table_view = EquipmentTableView(
                f"{equipment_model.data(equipment_model.index(x, 0), 0)}",  # タイトルを設定
                proxy_model,
            )  # QTableViewのインスタンスを作成
            self.multi_table_views.append(table_view)  # リストに追加
            self.multi_column_layout.addWidget(table_view)  # レイアウトに追加

        proxy_model = QSortFilterProxyModel()

        proxy_model.setSourceModel(equipment_model)  # 元のModelをセット

        # ★ 1. 検索対象の「列番号（0始まり）」を指定する（例: 2列目を対象にする）
        proxy_model.setFilterKeyColumn(1)

        self.table1_view = EquipmentTableView(
            "Table 1", equipment_model
        )  # QTableViewのインスタンスを作成

        self.table2_view = EquipmentTableView(
            "Table 2", proxy_model
        )  # QTableViewのインスタンスを作成

        self.table3_view = EquipmentTableView(
            "Table 3", equipment_model
        )  # QTableViewのインスタンスを作成

        self.h_layout.addLayout(
            self.multi_column_layout
        )  # レイアウトに垂直レイアウトを追加
        self.h_layout.addWidget(self.table1_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table2_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table3_view)  # レイアウトにQTableViewを追加
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(10)  # レイアウトの余白を10に設定

        self.setLayout(self.h_layout)  # 垂直レイアウトに水平レイアウトを追
