import pytest
from graph.const import *

from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    Equipment,
    NodeType,
    Port,
    PortDirection,
    PortGender,
)
from live_line_builder.ui.models.patch_table_model import PatchTableModel


@pytest.fixture
def patch_system(qapp):
    """
    各テストで共通して使用する初期状態のシステム(Fixture)
    元のコードのヒント「4. テスト用シナリオ」に沿ったデータを準備します。
    """
    sys = AudioPatchSystem()

    # --- [Arrange] 事前データの準備 ---
    sys.add_equipment(Equipment(EQ_VO, "Vo.Mic", NodeType.MIC))
    sys.add_equipment(Equipment(EQ_LG, "LG.Amp", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment(EQ_LG_MIC, "LG.Mic", NodeType.MIC))
    sys.add_equipment(Equipment(EQ_SB, "StageBox16", NodeType.STAGE_BOX))
    sys.add_equipment(Equipment(EQ_MIX, "MG24/14FX Console", NodeType.MIXER))

    # 楽器ポート
    sys.add_port(Port(VO_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_VO))
    sys.add_port(Port(LG_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_LG))
    sys.add_port(
        Port(LG_MIC_IN, "IN", PortDirection.IN, PortGender.FEMALE, EQ_LG_MIC, 1)
    )
    sys.add_port(
        Port(LG_MIC_OUT, "Out", PortDirection.OUT, PortGender.MALE, EQ_LG_MIC, 1)
    )

    # StageBox Ch1 (Vo用)
    sys.add_port(Port(SB_IN1, "Ch1 In", PortDirection.IN, PortGender.FEMALE, EQ_SB, 1))
    sys.add_port(Port(SB_OUT1, "Ch1 Out", PortDirection.OUT, PortGender.MALE, EQ_SB, 1))

    # StageBox Ch2 (Gt用)
    sys.add_port(Port(SB_IN2, "Ch2 In", PortDirection.IN, PortGender.FEMALE, EQ_SB, 2))
    sys.add_port(Port(SB_OUT2, "Ch2 Out", PortDirection.OUT, PortGender.MALE, EQ_SB, 2))

    # ミキサー入力
    sys.add_port(
        Port(MIX_IN1, "Ch1 In", PortDirection.IN, PortGender.FEMALE, EQ_MIX, 1)
    )
    sys.add_port(
        Port(MIX_IN2, "Ch2 In", PortDirection.IN, PortGender.FEMALE, EQ_MIX, 2)
    )

    # テスト用のAux出力(オス) - 性別エラー検証用
    sys.add_port(
        Port(MIX_AUX1_OUT, "Aux1 Out", PortDirection.OUT, PortGender.MALE, EQ_MIX)
    )

    return sys


def test_generate_model(patch_system):
    """PatchTableViewがequipment視点で動作するか確認"""
    PatchTableModel(patch_system, EQ_SB)


def test_get_model_column_length(patch_system):
    model = PatchTableModel(patch_system, EQ_SB)
    assert model.columnCount() == 6
