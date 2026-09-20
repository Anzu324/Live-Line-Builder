import pytest
from pydantic import ValidationError

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
    EquipmentPortRow,
    EquipmentRow,
    SetListEntity,
    SetListRow,
)


def test_equipment_row_types():
    """EquipmentRow の型定義および自動変換・バリデーションのテスト"""
    # 正常系: 文字列 "5" が自動的に int(5) に変換される
    row = EquipmentRow(
        equip_id="eq01",
        name="SM58",
        equip_type="Mic",
        quantity="5",  # type: ignore[arg-type]
    )
    assert row.quantity == 5
    assert isinstance(row.quantity, int)
    assert row.name == "SM58"

    # 代入時の自動変換
    row.quantity = "10"  # type: ignore[assignment]
    assert row.quantity == 10
    assert isinstance(row.quantity, int)

    # 不正な値の代入拒否 (int に変換できない文字列)
    with pytest.raises(ValidationError):
        row.quantity = "not_a_number"  # type: ignore[assignment]


def test_equipment_row_dict_compatibility():
    """Pydantic行モデルの辞書ライクアクセスの互換性テスト"""
    row = EquipmentRow(
        equip_id="eq01",
        name="SM58",
        equip_type="Mic",
        quantity=2,
    )
    # __getitem__ によるアクセス
    assert row["equip_id"] == "eq01"
    assert row["quantity"] == 2

    # __contains__ による存在確認
    assert "equip_id" in row
    assert "quantity" in row
    assert "unknown_field" not in row

    # __setitem__ による更新
    row["name"] = "Beta58"
    assert row.name == "Beta58"
    assert row["name"] == "Beta58"


def test_table_entity_init_and_access():
    """TableEntityの初期化とアクセスのテスト"""
    # 辞書のリストから初期化できる
    entity = EquipmentDefinition(
        rows=[
            {"equip_id": "eq01", "name": "Mic A", "equip_type": "Mic", "quantity": "3"},
            {"equip_id": "eq02", "name": "Amp B", "equip_type": "Amp", "quantity": 1},
        ]
    )

    assert len(entity) == 2
    assert entity.count_column() == 4

    # 1行目の quantity が int(3) に自動変換されていること
    assert entity[0, "quantity"] == 3
    assert isinstance(entity[0, "quantity"], int)
    assert entity.get_value(0, 3) == 3

    # 行オブジェクト経由のアクセス
    row0 = entity.get_row(0)
    assert isinstance(row0, EquipmentRow)
    assert row0.name == "Mic A"
    assert row0.quantity == 3


def test_table_entity_set_value_type_coercion_and_validation():
    """set_value による型変換と不正値の拒否テスト"""
    entity = EquipmentDefinition(
        rows=[
            {"equip_id": "eq01", "name": "Mic A", "equip_type": "Mic", "quantity": 1},
        ]
    )

    # 1. 数量(quantity: int, 列インデックス 3) に文字列 "42" を設定 -> 成功し int(42) になる
    success = entity.set_value(0, 3, "42")
    assert success is True
    assert entity[0, "quantity"] == 42
    assert isinstance(entity[0, "quantity"], int)

    # 2. 数量に変換不能な文字列 "abc" を設定 -> 失敗し値は維持される
    success = entity.set_value(0, 3, "abc")
    assert success is False
    assert entity[0, "quantity"] == 42  # 変更されていないこと

    # 3. editable=False のカラム (equip_id, 列インデックス 0) への変更は拒否される
    success = entity.set_value(0, 0, "eq99")
    assert success is False
    assert entity[0, "equip_id"] == "eq01"

    # 4. __setitem__ 経由での更新
    entity[0, "name"] = "Wireless Mic"
    assert entity[0, "name"] == "Wireless Mic"


def test_equipment_port_entity():
    """EquipmentPortEntity のテスト"""
    port_entity = EquipmentPortDefinition(
        rows=[
            {
                "port_id": "p01",
                "equip_id": "eq01",
                "name": "Out 1",
                "connector": "XLR",
                "flow": "OUT",
            }
        ]
    )

    assert len(port_entity) == 1
    row = port_entity.get_row(0)
    assert isinstance(row, EquipmentPortRow)
    assert row.connector == "XLR"
    assert row["connector"] == "XLR"


def test_setlist_entity():
    """SetListEntity のテスト"""
    setlist = SetListEntity(
        rows=[
            {
                "slot": "1",
                "group": "Band A",
                "start": "10:00",
                "time": "30min",
                "remark": "Opening",
            }
        ]
    )

    assert len(setlist) == 1
    row = setlist.get_row(0)
    assert isinstance(row, SetListRow)
    assert row.group == "Band A"


def test_table_entity_coerces_dict_rows_to_row_model():
    """辞書のまま受け取った行データが RowT に正規化されることを確認する"""
    entity = EquipmentDefinition(
        rows=[
            {
                "equip_id": "eq01",
                "name": "Mic A",
                "equip_type": "Mic",
                "quantity": "3",
            }
        ]
    )

    assert len(entity) == 1
    assert isinstance(entity.get_row(0), EquipmentRow)
    assert entity.get_row(0).quantity == 3
    assert isinstance(entity.get_row(0).quantity, int)

    entity.append_row(
        {
            "equip_id": "eq02",
            "name": "Amp B",
            "equip_type": "Amp",
            "quantity": "2",
        }
    )

    assert isinstance(entity.get_row(1), EquipmentRow)
    assert entity.get_row(1).quantity == 2


def test_table_entity_coerces_dict_assignment_and_rejects_invalid_values():
    """代入経路でも dict を RowT に変換し、無効な値はバリデーションで拒否する"""
    entity = EquipmentDefinition(
        rows=[
            {
                "equip_id": "eq01",
                "name": "Mic A",
                "equip_type": "Mic",
                "quantity": 1,
            }
        ]
    )

    entity[0] = {
        "equip_id": "eq02",
        "name": "Mic B",
        "equip_type": "Mic",
        "quantity": "5",
    }

    assert isinstance(entity.get_row(0), EquipmentRow)
    assert entity[0, "equip_id"] == "eq02"
    assert entity[0, "quantity"] == 5
    assert isinstance(entity[0, "quantity"], int)

    with pytest.raises(ValidationError):
        entity.set_row(
            0,
            {"equip_id": "eq03", "name": "Bad", "equip_type": "Mic", "quantity": "abc"},
        )

    assert entity[0, "quantity"] == 5
