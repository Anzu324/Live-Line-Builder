from .table_entity import Column

EQUIPMENT_COLUMNS = [
    Column(key="equip_id", header="EQUIPMENT", editable=False),
    Column(key="name", header="NAME"),
    Column(key="equip_type", header="TYPE"),
    Column(key="quantity", header="数量", default=1),
]

EQUIPMENT_PORT_COLUMNS = [
    Column(key="port_id", header="PORT", editable=False),
    Column(key="name", header="NAME"),
    Column(key="equip_id", header="EQUIP"),
    Column(key="connector", header="CON"),
    Column(key="flow", header="流れ"),
]

EQUIPMENT_INNER_LINKS_COLUMNS = [
    Column(key="equip_id", header="機材", editable=False),
    Column(key="input_port", header="入力"),
    Column(key="output_ports", header="出力"),
]

SETLIST_COLUMNS = [
    Column(key="slot", header="SONG", editable=False),
    Column(key="group", header="BAND"),
    Column(key="start", header="START"),
    Column(key="time", header="TIME"),
    Column(key="remark", header="REMARK", default=""),
]
