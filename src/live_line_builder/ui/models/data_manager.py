from pathlib import Path

from PySide6.QtCore import QObject, Signal

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
    PerformanceGroup,
)
from live_line_builder.domain.entities.columns import (
    EQUIPMENT_COLUMNS,
    EQUIPMENT_PORT_COLUMNS,
)
from live_line_builder.domain.entities.table_entity import zip_column_key_and_table
from live_line_builder.storages.repository import ProjectRepository


# TODO:公演ごとにもろもろを切り替える処理
class DataManager(QObject):
    """
    ModelやUIから呼び出され複数のエンティティ(ピュアなデータ)間の橋渡しを担う。
    """

    call_reload_all_ui = Signal()

    _equipment_entity: EquipmentDefinition
    _equipment_port_entity: EquipmentPortDefinition
    _performance_group_list: list[PerformanceGroup]

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
            self._equipment_entity = EquipmentDefinition(
                zip_column_key_and_table(temp, equipment_list)
            )
        temp = [i.key for i in EQUIPMENT_PORT_COLUMNS]
        if not (equipment_ports is None):
            self._equipment_port_entity = EquipmentPortDefinition(
                zip_column_key_and_table(temp, equipment_ports)
            )

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> DataManager:
        print("DataManaferのMockのfactoryを呼んでいる。")
        dm = DataManager()
        dm.load_mock_project()
        return dm
        #return DataManager(None, mock_data.equipment_data, mock_data.port_data)

    @property
    def equipment_entity(self) -> EquipmentDefinition:
        return self._equipment_entity

    @property
    def equipment_port_entity(self) -> EquipmentPortDefinition:
        return self._equipment_port_entity

    def load_projetct_from_save_data(self, file_path: Path):
        repository = ProjectRepository()
        equipment_entity, equipment_port_entity, performance_groups = repository.load(
            file_path
        )
        self._equipment_entity = equipment_entity
        self._equipment_port_entity = equipment_port_entity
        self._performance_group_list = performance_groups

        self.call_reload_all_ui.emit()

    def load_mock_project(self, mock_file_name: str = "full_mock_data.json"):
        repository = ProjectRepository()
        equipment_entity, equipment_port_entity, performance_groups = repository.load_mock(
            mock_file_name
        )
        self._equipment_entity = equipment_entity
        self._equipment_port_entity = equipment_port_entity
        self._performance_group_list = performance_groups

        self.call_reload_all_ui.emit()

    def __repr__(self) -> str:
        return f"DataManager(equipment_entity={self._equipment_entity}, equipment_port_entity={self._equipment_port_entity}, performance_group_list={self._performance_group_list})"
