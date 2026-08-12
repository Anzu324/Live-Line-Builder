from PySide6.QtCore import QObject, Signal

from app_mock import mock_data

from .equipment_model import EquipmentConnectorModel, EquipmentModel


# ★ QObject を継承する
class DataManager(QObject):
    # ★ カスタムシグナルの定義（QObject の直下に書く）
    data_changed = Signal()  # 引数なしの通知
    product_added = Signal(dict)  # 追加された商品データ（dict）を飛ばす通知

    def __init__(
        self,
        parent=None,
        equipments: list[list[str]] | None = None,
        equipmentconnectors: list[list[str]] | None = None,
    ):
        # ★ 親クラス（QObject）の初期化を必ず呼ぶ！
        super().__init__(parent)

        # 文字列で機器表を初期化する
        if equipments is None:
            self._equipments = EquipmentModel()
        else:
            self._equipments = EquipmentModel(equipments)

        # 文字列でコネクター表を初期化する。
        if equipmentconnectors is None:
            self._equipmentconnectors = EquipmentConnectorModel()
        else:
            self._equipmentconnectors = EquipmentConnectorModel(equipmentconnectors)

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> DataManager:
        return DataManager(None, mock_data.equipment_data, mock_data.connector_data)

    @property
    def equipments(self):
        return self._equipments

    @property
    def equipmentconnectors(self):
        return self._equipmentconnectors

    # def add_product(self, product_data: dict):
    #     """商品追加と同時にシグナルを発火する"""
    #     self._products.append(product_data)

    #     # ★ シグナルを発火（通知）！
    #     self.product_added.emit(product_data)
    #     self.data_changed.emit()
