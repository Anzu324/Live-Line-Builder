import pytest
from graph.const import *
from PySide6.QtCore import Qt

from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    EquipmentCategory,
    EquipmentInstance,
    PortDirection,
    PortGender,
    PortInstance,
)
from live_line_builder.ui.models.audio_patch_model import PatchTableModel, Stream


@pytest.fixture
def patch_system(qapp):
    """
    各テストで共通して使用する初期状態のシステム(Fixture)
    元のコードのヒント「4. テスト用シナリオ」に沿ったデータを準備します。
    """
    sys = AudioPatchSystem()

    # --- [Arrange] 事前データの準備 ---
    sys._add_equipment(EquipmentInstance(EQ_VO, "Vo.Mic", EquipmentCategory.MIC))
    sys._add_equipment(EquipmentInstance(EQ_LG, "LG.Amp", EquipmentCategory.INSTRUMENT))
    sys._add_equipment(EquipmentInstance(EQ_LG_MIC, "LG.Mic", EquipmentCategory.MIC))
    sys._add_equipment(
        EquipmentInstance(EQ_SB, "MultiBox16", EquipmentCategory.MULTI_BOX)
    )
    sys._add_equipment(
        EquipmentInstance(EQ_MIX, "MG24/14FX Console", EquipmentCategory.MIXER)
    )

    # 楽器ポート
    sys._add_port(
        PortInstance(VO_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_VO)
    )
    sys._add_port(
        PortInstance(LG_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_LG)
    )
    sys._add_port(
        PortInstance(LG_MIC_IN, "IN", PortDirection.IN, PortGender.FEMALE, EQ_LG_MIC, 1)
    )
    sys._add_port(
        PortInstance(
            LG_MIC_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_LG_MIC, 1
        )
    )

    # StageBox Ch1 (Vo用)
    sys._add_port(
        PortInstance(SB_IN1, "Ch1 In", PortDirection.IN, PortGender.FEMALE, EQ_SB, 1)
    )
    sys._add_port(
        PortInstance(SB_OUT1, "Ch1 Out", PortDirection.OUT, PortGender.MALE, EQ_SB, 1)
    )

    # StageBox Ch2 (Gt用)
    sys._add_port(
        PortInstance(SB_IN2, "Ch2 In", PortDirection.IN, PortGender.FEMALE, EQ_SB, 2)
    )
    sys._add_port(
        PortInstance(SB_OUT2, "Ch2 Out", PortDirection.OUT, PortGender.MALE, EQ_SB, 2)
    )

    # ミキサー入力
    sys._add_port(
        PortInstance(MIX_IN1, "Ch1 In", PortDirection.IN, PortGender.FEMALE, EQ_MIX, 1)
    )
    sys._add_port(
        PortInstance(MIX_IN2, "Ch2 In", PortDirection.IN, PortGender.FEMALE, EQ_MIX, 2)
    )

    # テスト用のAux出力(オス) - 性別エラー検証用
    sys._add_port(
        PortInstance(
            MIX_AUX1_OUT, "Aux1 Out", PortDirection.OUT, PortGender.MALE, EQ_MIX
        )
    )

    return sys


def test_generate_model(patch_system):
    """PatchTableViewがequipment視点で動作するか確認"""
    PatchTableModel(patch_system, EQ_SB)


def test_get_model_column_length(patch_system):
    model = PatchTableModel(patch_system, EQ_SB)
    model.change_base_point(EQ_SB, Stream.INPUT)
    assert model.columnCount() == 3


def test_model_data_returns_port_name(patch_system):
    model = PatchTableModel(patch_system, EQ_SB)
    model.change_base_point(EQ_SB, Stream.INPUT)

    value = model.data(model.index(0, 0), Qt.DisplayRole)

    assert isinstance(value, str)
    assert value
