from __future__ import annotations

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentInnerLinksDefinition,
    EquipmentInnerLinksRow,
    EquipmentPortDefinition,
    EquipmentPortRow,
    EquipmentRow,
)

from .audio_patch import (
    AudioPatchSystem,
    EquipmentDTO,
    EquipmentID,
    EquipmentInstance,
    NodeType,
    PortDirection,
    PortGender,
    PortID,
    PortInstance,
)


def _coerce_node_type(value: str) -> NodeType:
    """文字列の機材種別を NodeType に変換する。"""
    normalized = value.strip().lower()

    if normalized in {"mic", "microphone"}:
        return NodeType.MIC
    if normalized in {"instrument", "guitar", "bass", "keyboard", "drum"}:
        return NodeType.INSTRUMENT
    if normalized in {"stagebox", "stage_box", "multicore", "multibox"}:
        return NodeType.MULTI_BOX
    if normalized in {"mixer", "console"}:
        return NodeType.MIXER
    if normalized in {"processor", "fx", "effect"}:
        return NodeType.PROCESSOR
    if normalized in {"main amp", "main_amp", "poweramp", "amp"}:
        return NodeType.MAIN_AMP
    if normalized in {"speaker", "cabinet"}:
        return NodeType.SPEAKER

    return NodeType.INSTRUMENT


def _coerce_port_direction(flow: str) -> PortDirection:
    """外部定義の flow 文字列から PortDirection を作る。"""
    if flow.strip().upper() == "OUT":
        return PortDirection.OUT
    return PortDirection.IN


def _coerce_port_gender(flow: str) -> PortGender:
    """現状の簡易ルール: OUT は Male, IN は Female と扱う。"""
    return (
        PortGender.MALE
        if _coerce_port_direction(flow) == PortDirection.OUT
        else PortGender.FEMALE
    )


def _coerce_port_channel_no(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except TypeError, ValueError:
        return None


# XXX:実装途中エラーのみ解消。
def build_equipment_instance(
    equipment_definition: EquipmentRow,
    ports: EquipmentDefinition,
    inner_links: EquipmentInnerLinksDefinition,
) -> EquipmentDTO:
    eq_instance = EquipmentInstance(
        EquipmentID(equipment_definition.equip_id),
        equipment_definition.name,
        NodeType(equipment_definition.equip_type),
    )
    fileterd_ports: list[EquipmentPortRow] = [
        ports[i]
        for i in range(ports.column_size())
        if ports.get_item(i, "equip_id")
        == equipment_definition.name  # 対象機材のコネクタのみを絞って検索
    ]
    ports_instances = {
        PortID(i.port_id): PortInstance(
            id=PortID(i.port_id),
            name=i.name,
            direction=PortDirection.IN,
            gender=PortGender.MALE,
            equipment_id=EquipmentID(i.equip_id),
            channel_no=None,
        )
        for i in fileterd_ports
    }

    fileterd_links: list[EquipmentInnerLinksRow] = [
        inner_links[i]
        for i in range(inner_links.column_size())
        if inner_links.get_item(i, "equip_id")
        == equipment_definition.name  # 対象機材のコネクタのみを絞って検索
    ]
    forward_inner_links = {
        PortID(i.input_port): {PortID(j) for j in i.output_ports}
        for i in fileterd_links
    }

    return EquipmentDTO(eq_instance, ports_instances, forward_inner_links, dict())


def register_equipment_definition(
    system: AudioPatchSystem,
    equipment_definition: EquipmentDefinition,
    port_definition: EquipmentPortDefinition | None = None,
) -> None:
    """既存の AudioPatchSystem に機材定義を登録する。"""
    for equip_row in equipment_definition.rows:
        equipment = EquipmentInstance(
            id=EquipmentID(equip_row.equip_id),
            name=equip_row.name,
            type=_coerce_node_type(equip_row.equip_type),
        )
        system._add_equipment(equipment)

    if port_definition is not None:
        for port_row in port_definition.rows:
            port = PortInstance(
                id=PortID(port_row.port_id),
                name=port_row.name,
                direction=_coerce_port_direction(port_row.flow),
                gender=_coerce_port_gender(port_row.flow),
                equipment_id=EquipmentID(port_row.equip_id),
                channel_no=_coerce_port_channel_no(port_row.get("channel_no", None)),
            )
            system._add_port(port)
