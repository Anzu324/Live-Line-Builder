from PySide6.QtCore import QObject, Signal

from live_line_builder.app_mock import mock_data
from live_line_builder.domain.entities import PerformanceEntity, ProjectDataEntity
from live_line_builder.ui.models import DataManager, EquipmentModel, EquipmentPortModel
from live_line_builder.ui.views import MainContentView, MainWindow


# ★ QObject を継承する
class AppController(QObject):
    """
    main_windowに代わってモデルの配線を担当。
    """

    # ★ カスタムシグナルの定義（QObject の直下に書く）
    data_changed = Signal()  # 引数なしの通知
    product_added = Signal(dict)  # 追加された商品データ（dict）を飛ばす通知
    _data_mangeger: DataManager

    def __init__(
        self,
        parent=None,
        equipment_list: list[list[str]] | None = None,
        equipment_ports: list[list[str]] | None = None,
    ):
        # 親クラスのQObjectのご加護を得る
        super().__init__(parent)

        self.project_datum = ProjectDataEntity()
        self.performance_data = [PerformanceEntity()]

        self._data_mangeger = DataManager(
            self, equipment_list=equipment_list, equipment_ports=equipment_ports
        )

        # 文字列で機器表を初期化する
        self._equipments = EquipmentModel(self._data_mangeger.equipment_entity)

        # 文字列でコネクター表を初期化する。
        self._equipment_ports = EquipmentPortModel(
            self._data_mangeger.equipment_port_entity
        )

        self.central_widget = MainContentView(
            self._equipments,
            self._equipment_ports,
            [1, 2],  # 例: 列0と列1をフィルター対象とする
        )  # メインコンテンツビューの作成

        self.main_window = (
            MainWindow()
        )  # selfをつけ生存期間をAppCOntorollerと同等に延長
        self.main_window.set_central_widget(self.central_widget)  # 埋め込み
        self.main_window.show()  # 表示

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> AppController:
        print("AppControllerのfactoryを呼んでいる。早めに移行せよ")
        return AppController(None, mock_data.equipment_data, mock_data.port_data)

    @property
    def equipments(self):
        return self._equipments

    @property
    def equipment_ports(self):
        return self._equipment_ports

    @property
    def data_mangeger(self):
        return self._data_mangeger

    # def add_product(self, product_data: dict):
    #     """商品追加と同時にシグナルを発火する"""
    #     self._products.append(product_data)

    #     # ★ シグナルを発火（通知）！
    #     self.product_added.emit(product_data)
    #     self.data_changed.emit()
