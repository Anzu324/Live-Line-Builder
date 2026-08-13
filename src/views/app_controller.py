from PySide6.QtCore import QObject, Signal

from app_mock import mock_data

from ..models.equipment_model import EquipmentModel, EquipmentPortModel
from ..models.performance_model import PerformanceModel
from ..models.project_data_model import ProjectDataModel


# ★ QObject を継承する
class AppController(QObject):
    """
    main_windowに代わってモデルの配線を担当。
    """

    # ★ カスタムシグナルの定義（QObject の直下に書く）
    data_changed = Signal()  # 引数なしの通知
    product_added = Signal(dict)  # 追加された商品データ（dict）を飛ばす通知

    def __init__(
        self,
        parent=None,
        equipment_list: list[list[str]] | None = None,
        equipment_ports: list[list[str]] | None = None,
    ):
        # ★ 親クラス（QObject）の初期化を必ず呼ぶ！
        super().__init__(parent)

        self.project_datum = ProjectDataModel()
        self.performance_data = [PerformanceModel()]

        # 文字列で機器表を初期化する
        if equipment_list is None:
            self._equipments = EquipmentModel()
        else:
            self._equipments = EquipmentModel(equipment_list)

        # 文字列でコネクター表を初期化する。
        if equipment_ports is None:
            self._equipment_ports = EquipmentPortModel()
        else:
            self._equipment_ports = EquipmentPortModel(equipment_ports)

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> AppController:
        return AppController(None, mock_data.equipment_data, mock_data.port_data)

    @property
    def equipments(self):
        return self._equipments

    @property
    def equipment_ports(self):
        return self._equipment_ports

    # def add_product(self, product_data: dict):
    #     """商品追加と同時にシグナルを発火する"""
    #     self._products.append(product_data)

    #     # ★ シグナルを発火（通知）！
    #     self.product_added.emit(product_data)
    #     self.data_changed.emit()
