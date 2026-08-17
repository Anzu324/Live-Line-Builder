from .columns import EQUIPMENT_COLUMNS, EQUIPMENT_PORT_COLUMNS
from .table_entity import TableEntity


class EquipmentEntity(TableEntity):
    """機材情報テーブル"""

    columns = EQUIPMENT_COLUMNS


class EquipmentPortEntity(TableEntity):
    """機材コネクタ情報テーブル"""

    columns = EQUIPMENT_PORT_COLUMNS
