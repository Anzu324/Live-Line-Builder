from pathlib import Path

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
)
from live_line_builder.storages.repository import ProjectRepository


def test_repository_load_mock_data_structure():
    """RepositoryがモックJSONを読むことでProjectDataCargoを返せることを確認する"""
    repository = ProjectRepository()
    cargo = repository.load_mock()

    assert isinstance(cargo.equipment_entity, EquipmentDefinition)
    assert isinstance(cargo.equipment_port_entity, EquipmentPortDefinition)
    assert isinstance(cargo.performance_group_list, list)
    assert len(cargo.performance_group_list) == 2


def test_repository_save_and_load(tmp_path: Path):
    """RepositoryがファイルI/Oとシリアライズの両方を扱えることを確認する"""
    repository = ProjectRepository()
    cargo = repository.load_mock()
    save_file = tmp_path / "test_saved_project.json"

    repository.save(
        cargo.equipment_entity,
        cargo.equipment_port_entity,
        cargo.performance_group_list,
        save_file,
    )

    assert save_file.exists()

    loaded = repository.load(save_file)

    assert len(loaded.equipment_entity.rows) == len(cargo.equipment_entity.rows)
    assert len(loaded.equipment_port_entity.rows) == len(
        cargo.equipment_port_entity.rows
    )
    assert len(loaded.performance_group_list) == len(cargo.performance_group_list)
    assert (
        loaded.performance_group_list[0]._performance_info.name
        == cargo.performance_group_list[0]._performance_info.name
    )
    assert (
        loaded.performance_group_list[0]._performance_info.place
        == cargo.performance_group_list[0]._performance_info.place
    )
