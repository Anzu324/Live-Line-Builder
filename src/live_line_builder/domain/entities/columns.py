from .table_entity import Column

EQUIPMENT_COLUMNS = [
    Column(key="equip_id", header="EQUIPMENT", data_type=str, editable=False),
    Column(key="name", header="NAME", data_type=str),
    Column(key="type", header="TYPE", data_type=str, default=100),
    Column(key="quantity", header="数量", data_type=str, default=100),
]

EQUIPMENT_PORT_COLUMNS = [
    Column(key="port_id", header="PORT", data_type=str, editable=False),
    Column(key="name", header="NAME", data_type=str),
    Column(key="equip_id", header="EQUIP", data_type=str, default=100),
    Column(key="connerctor", header="CON", data_type=str, default=100),
    Column(key="flow", header="流れ", data_type=str, default=100),
]
