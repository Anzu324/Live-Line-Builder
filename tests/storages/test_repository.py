from pathlib import Path

import pytest

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
    PerformanceGroup,
)
from live_line_builder.domain.line_graph.audio_patch import NodeType
from live_line_builder.storages.serializer import ProjectSerializer


@pytest.fixture
def repository():
    return ProjectSerializer()


def test_load_mock_data_structure(repository):
    """load_mock() を呼び出して、各EntityおよびPerformanceGroupが取得できるかテスト"""
    equip_entity, port_entity, perf_groups = repository.load_mock()

    assert isinstance(equip_entity, EquipmentDefinition)
    assert isinstance(port_entity, EquipmentPortDefinition)
    assert isinstance(perf_groups, list)
    assert len(perf_groups) == 2


def test_equipment_and_port_entities(repository):
    """機材テーブル・ポートテーブルの内容および紐付けをテスト"""
    equip_entity, port_entity, _ = repository.load_mock()

    # 機材テーブルの検証 (5件登録されている)
    assert len(equip_entity.rows) == 5
    equip_ids = [row["equip_id"] for row in equip_entity.rows]
    assert "equip_0001" in equip_ids
    assert "equip_0002" in equip_ids
    assert "equip_0003" in equip_ids
    assert "equip_0004" in equip_ids
    assert "equip_0005" in equip_ids

    # ポートテーブルの検証 (全27ポート)
    assert len(port_entity.rows) == 27
    for port_row in port_entity.rows:
        # すべてのポートに親のequip_idが付与されていること
        assert "equip_id" in port_row
        assert port_row["equip_id"] in equip_ids
        assert "port_id" in port_row
        assert "name" in port_row
        assert "connector" in port_row
        assert "flow" in port_row

    # 特定の機材（MG24/14FX）のポート数確認（12ポート）
    mg24_ports = [p for p in port_entity.rows if p["equip_id"] == "equip_0001"]
    assert len(mg24_ports) == 12


def test_performance_group_loaded(repository):
    """公演情報およびAudioPatchSystemの復元状態をテスト"""
    _, _, perf_groups = repository.load_mock()

    # Day 1 の検証
    day1: PerformanceGroup = perf_groups[0]
    info1 = day1._performance_info
    assert info1.tab_name == "Day 1"
    assert info1.name == "Summer Music Fest 2026"
    assert info1.place == "Main Stage"
    assert info1.day == "2026-08-01"
    assert info1.live_director == "山田太郎"
    assert info1.sound_director == "佐藤音響"
    assert info1.sound_crews == "鈴木, 田中"

    # Day 1 のパッチシステム機器
    patch_sys1 = day1._audiopatch
    assert len(patch_sys1.equipments) == 4
    assert "patch_eq_vo1" in patch_sys1.equipments
    assert patch_sys1.equipments["patch_eq_vo1"].type == NodeType.MIC
    assert patch_sys1.equipments["patch_eq_console"].type == NodeType.MIXER

    # Day 1 のパッチシステム結線
    # vo1_out -> sb_in1
    assert "vo1_out" in patch_sys1.ports
    assert "sb_in1" in patch_sys1.ports
    assert "sb_in1" in patch_sys1.forward_edges["vo1_out"]
    assert patch_sys1.backward_edges["sb_in1"] == "vo1_out"

    # sb_out1 -> console_ch1_in
    assert "console_ch1_in" in patch_sys1.forward_edges["sb_out1"]
    assert patch_sys1.backward_edges["console_ch1_in"] == "sb_out1"

    # Day 2 の検証
    day2: PerformanceGroup = perf_groups[1]
    info2 = day2._performance_info
    assert info2.tab_name == "Day 2"
    assert info2.name == "Summer Music Fest 2026 Day2"
    assert len(day2._audiopatch.equipments) == 2


def test_save_and_reload(repository, tmp_path: Path):
    """save() で保存したJSONを再度 load() して完全復元できるかテスト"""
    equip_entity, port_entity, perf_groups = repository.load_mock()

    save_file = tmp_path / "test_saved_project.json"
    repository.save(save_file, equip_entity, port_entity, perf_groups)

    assert save_file.exists()

    # 保存したファイルを再読込
    loaded_equip, loaded_port, loaded_groups = repository.load(save_file)

    assert len(loaded_equip.rows) == len(equip_entity.rows)
    assert len(loaded_port.rows) == len(port_entity.rows)
    assert len(loaded_groups) == len(perf_groups)

    # 公演情報の復元チェック
    assert (
        loaded_groups[0]._performance_info.name == perf_groups[0]._performance_info.name
    )
    assert (
        loaded_groups[0]._performance_info.place
        == perf_groups[0]._performance_info.place
    )

    # パッチ結線の復元チェック
    reloaded_sys = loaded_groups[0]._audiopath
    assert "sb_in1" in reloaded_sys.forward_edges["vo1_out"]
    assert reloaded_sys.backward_edges["sb_in1"] == "vo1_out"
