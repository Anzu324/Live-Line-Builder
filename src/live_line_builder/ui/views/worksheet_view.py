from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from live_line_builder.ui.models import EquipmentModel, EquipmentPortModel
from live_line_builder.ui.models.proxies import (
    MultiFilterProxyModel,  # プロキシモデルをインポート
)
from live_line_builder.ui.views.live_info_view import LiveInfoView
from live_line_builder.ui.views.table import (
    EquipmentTableView,  # テーブルビューをインポート
)


# メインコンテンツビューのクラス
# メインコンテンツビューとは、中央にある、図や表を表示する為のウィジェットです。
class WorkSheetView(QWidget):
    view_tab_name = "仕込み図"  # タブ名を設定

    def __init__(
        self,
        equipment_model: EquipmentModel,
        connector_model: EquipmentPortModel,
        multi_id_list: list[int],
        parent=None,
    ):
        super().__init__(parent)
        self.v_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout(self)  # 垂直方向のレイアウトを作成

        # ライブ情報エリア
        self.form = LiveInfoView()
        self.v_layout.addWidget(self.form)

        # 回線エリア
        self.multi_column_layout = QVBoxLayout()  # マルチの列のレイアウトを作成
        self.multi_column_layout.setContentsMargins(0, 0, 0, 0)
        self.multi_column_layout.setSpacing(1)  # レイアウトの余白を1に設定
        self.multi_table_views = []  # マルチの列のテーブルビューを保持するリスト

        for x in multi_id_list:
            proxy_model = MultiFilterProxyModel()
            proxy_model.setSourceModel(connector_model)  # 元のModelをセット
            if i := equipment_model.get_product_at(x):
                print(
                    f"Creating table for equipment ID: {x}:{i['name']}"
                )  # デバッグ用の出力
                proxy_model.set_filter_condition(
                    0, str(i["equip_id"])
                )  # フィルター対象の列と値を指定

            if proxy_model.rowCount() == 0:
                break  # コネクターが一つも無いものを自動的に除外する。

            table_view = EquipmentTableView(
                f"{equipment_model.data(equipment_model.index(x, 0), 0)}",  # タイトルを設定
                proxy_model,
            )  # QTableViewのインスタンスを作成
            self.multi_table_views.append(table_view)  # リストに追加
            self.multi_column_layout.addWidget(table_view)  # レイアウトに追加

        self.table1_view = EquipmentTableView(
            "Table 1", equipment_model
        )  # QTableViewのインスタンスを作成

        self.table3_view = EquipmentTableView(
            "Table 3", equipment_model
        )  # QTableViewのインスタンスを作成

        self.h_layout.addLayout(
            self.multi_column_layout
        )  # レイアウトに垂直レイアウトを追加
        self.h_layout.addWidget(self.table1_view)  # レイアウトにQTableViewを追加
        self.h_layout.addWidget(self.table3_view)  # レイアウトにQTableViewを追加
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(10)  # レイアウトの余白を10に設定
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)  # 垂直レイアウトに水平レイアウトを追
