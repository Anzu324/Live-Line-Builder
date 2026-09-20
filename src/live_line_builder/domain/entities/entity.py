from .columns import EQUIPMENT_COLUMNS, EQUIPMENT_PORT_COLUMNS, SETLIST_COLUMNS
from .table_entity import TableEntity, TableRowModel


class EquipmentRow(TableRowModel):
    """機材行モデルの列"""

    equip_id: str
    name: str
    equip_type: str
    quantity: int = 1


class EquipmentPortRow(TableRowModel):
    """機材ポート行モデル"""

    port_id: str
    name: str
    equip_id: str
    connector: str
    flow: str


class SetListRow(TableRowModel):
    """セットリスト行モデル"""

    slot: str
    group: str
    start: str
    time: str
    remark: str = ""


class EquipmentDefinition(TableEntity[EquipmentRow]):
    """機材情報テーブル"""

    row_type = EquipmentRow
    columns = EQUIPMENT_COLUMNS


class EquipmentPortDefinition(TableEntity[EquipmentPortRow]):
    """機材コネクタ情報テーブル"""

    row_type = EquipmentPortRow
    columns = EQUIPMENT_PORT_COLUMNS


class SetListEntity(TableEntity[SetListRow]):
    """セトリ情報テーブル"""

    row_type = SetListRow
    columns = SETLIST_COLUMNS
