import pytest
from graph.const import *

from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    EquipmentInstance,
    NodeType,
    PortDirection,
    PortGender,
    PortInstance,
)
from live_line_builder.ui.models.audio_patch_model import PatchTableModel


@pytest.fixture
def patch_system(qapp):
    """
    各テストで共通して使用する初期状態のシステム(Fixture)
    元のコードのヒント「4. テスト用シナリオ」に沿ったデータを準備します。
    """
    sys = AudioPatchSystem()

    # --- [Arrange] 事前データの準備 ---
    sys._add_equipment(EquipmentInstance(EQ_VO, "Vo.Mic", NodeType.MIC))
    sys._add_equipment(EquipmentInstance(EQ_LG, "LG.Amp", NodeType.INSTRUMENT))
    sys._add_equipment(EquipmentInstance(EQ_LG_MIC, "LG.Mic", NodeType.MIC))
    sys._add_equipment(EquipmentInstance(EQ_SB, "StageBox16", NodeType.STAGE_BOX))
    sys._add_equipment(EquipmentInstance(EQ_MIX, "MG24/14FX Console", NodeType.MIXER))

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
    assert model.columnCount() == 6
