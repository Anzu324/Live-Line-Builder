from PySide6.QtCore import QObject

from live_line_builder.app_mock import mock_data
from live_line_builder.domain.entities import EquipmentEntity, EquipmentPortEntity
from live_line_builder.domain.entities.columns import (
    EQUIPMENT_COLUMNS,
    EQUIPMENT_PORT_COLUMNS,
)
from live_line_builder.domain.entities.table_entity import zip_column_key_and_table


class DataManager(QObject):
    """
    ModelやUIから呼び出され複数のエンティティ(ピュアなデータ)間の橋渡しを担う。
    """

    _equipment_entity: EquipmentEntity
    _equipment_port_entity: EquipmentPortEntity

    def __init__(
        self,
        parent=None,
        equipment_list: list[list[str]] | None = None,
        equipment_ports: list[list[str]] | None = None,
    ) -> None:
        # 親クラスのQObjectのご加護を得る
        super().__init__(parent)
        temp = [i.key for i in EQUIPMENT_COLUMNS]
        if not (equipment_list is None):
            self._equipment_entity = EquipmentEntity(
                zip_column_key_and_table(temp, equipment_list)
            )
        temp = [i.key for i in EQUIPMENT_PORT_COLUMNS]
        if not (equipment_ports is None):
            self._equipment_port_entity = EquipmentPortEntity(
                zip_column_key_and_table(temp, equipment_ports)
            )

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> DataManager:
        print("AppControllerのfactoryを呼んでいる。早めに移行せよ")
        return DataManager(None, mock_data.equipment_data, mock_data.port_data)

    @property
    def equipment_entity(self) -> EquipmentEntity:
        return self._equipment_entity

    @property
    def equipment_port_entity(self) -> EquipmentPortEntity:
        return self._equipment_port_entity
