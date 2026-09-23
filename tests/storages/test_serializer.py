from pathlib import Path

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
    PerformanceGroup,
)
from live_line_builder.domain.line_graph.audio_patch import (
    EquipmentID,
    NodeType,
    PortID,
)
from live_line_builder.storages.serializer import ProjectSerializer


def test_serializer_load_mock_data_structure():
    """SerializerがJSONからProjectDataCargoへ変換できることを確認する"""
    serializer = ProjectSerializer()
    json_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "live_line_builder"
        / "app_mock"
        / "full_mock_data.json"
    )
    cargo = serializer.load(json_path.read_text(encoding="utf-8"))

    assert isinstance(cargo.equipment_entity, EquipmentDefinition)
    assert isinstance(cargo.equipment_port_entity, EquipmentPortDefinition)
    assert isinstance(cargo.performance_group_list, list)
    assert len(cargo.performance_group_list) == 2


def test_serializer_round_trip():
    """Serializerの dump/load が対の責務であることを確認する"""
    serializer = ProjectSerializer()
    json_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "live_line_builder"
        / "app_mock"
        / "full_mock_data.json"
    )
    original = serializer.load(json_path.read_text(encoding="utf-8"))

    json_str = serializer.dump(
        original.equipment_entity,
        original.equipment_port_entity,
        original.performance_group_list,
    )
    reloaded = serializer.load(json_str)

    assert len(reloaded.equipment_entity.rows) == len(original.equipment_entity.rows)
    assert len(reloaded.equipment_port_entity.rows) == len(
        original.equipment_port_entity.rows
    )
    assert len(reloaded.performance_group_list) == len(original.performance_group_list)
    assert (
        reloaded.performance_group_list[0]._performance_info.name
        == original.performance_group_list[0]._performance_info.name
    )


def test_performance_group_loaded():
    """公演情報とAudioPatchSystemが復元されることを確認する"""
    serializer = ProjectSerializer()
    json_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "live_line_builder"
        / "app_mock"
        / "full_mock_data.json"
    )
    cargo = serializer.load(json_path.read_text(encoding="utf-8"))

    day1: PerformanceGroup = cargo.performance_group_list[0]
    info1 = day1._performance_info
    assert info1.tab_name == "Day 1"
    assert info1.name == "Summer Music Fest 2026"
    assert info1.place == "Main Stage"
    assert info1.day == "2026-08-01"
    assert info1.live_director == "山田太郎"
    assert info1.sound_director == "佐藤音響"
    assert info1.sound_crews == "鈴木, 田中"

    patch_sys1 = day1._audiopatch
    assert len(patch_sys1.equipments) == 4
    assert "patch_eq_vo1" in patch_sys1.equipments
    assert patch_sys1.equipments[EquipmentID("patch_eq_vo1")].type == NodeType.MIC
    assert patch_sys1.equipments[EquipmentID("patch_eq_console")].type == NodeType.MIXER

    assert "vo1_out" in patch_sys1.ports
    assert "sb_in1" in patch_sys1.ports
    assert "sb_in1" in patch_sys1.forward_edges[PortID("vo1_out")]
    assert patch_sys1.backward_edges[PortID("sb_in1")] == "vo1_out"
    assert "console_ch1_in" in patch_sys1.forward_edges[PortID("sb_out1")]
    assert patch_sys1.backward_edges[PortID("console_ch1_in")] == "sb_out1"

    day2: PerformanceGroup = cargo.performance_group_list[1]
    info2 = day2._performance_info
    assert info2.tab_name == "Day 2"
    assert info2.name == "Summer Music Fest 2026 Day2"
    assert len(day2._audiopatch.equipments) == 2


def test_equipment_and_port_entities():
    """機材テーブル・ポートテーブルの内容と紐付けが保持されることを確認する"""
    serializer = ProjectSerializer()
    json_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "live_line_builder"
        / "app_mock"
        / "full_mock_data.json"
    )
    cargo = serializer.load(json_path.read_text(encoding="utf-8"))

    equip_entity = cargo.equipment_entity
    port_entity = cargo.equipment_port_entity

    assert len(equip_entity.rows) == 5
    equip_ids = [row["equip_id"] for row in equip_entity.rows]
    assert "equip_0001" in equip_ids
    assert "equip_0002" in equip_ids
    assert "equip_0003" in equip_ids
    assert "equip_0004" in equip_ids
    assert "equip_0005" in equip_ids

    assert len(port_entity.rows) == 27
    for port_row in port_entity.rows:
        assert "equip_id" in port_row
        assert port_row["equip_id"] in equip_ids
        assert "port_id" in port_row
        assert "name" in port_row
        assert "connector" in port_row
        assert "flow" in port_row

    mg24_ports = [p for p in port_entity.rows if p["equip_id"] == "equip_0001"]
    assert len(mg24_ports) == 12
