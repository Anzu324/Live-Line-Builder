import pytest

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
    sys.add_equipment(Equipment("eq_vo", "Vo.Mic", NodeType.MIC))
    sys.add_equipment(Equipment("eq_lg", "LG.Amp", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_lg_mic", "LG.Mic", NodeType.MIC))
    sys.add_equipment(Equipment("eq_sb", "StageBox16", NodeType.STAGE_BOX))
    sys.add_equipment(Equipment("eq_mix", "MG24/14FX Console", NodeType.MIXER))

    # 楽器ポート
    sys.add_port(Port("vo_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_vo"))
    sys.add_port(Port("lg_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_lg"))
    sys.add_port(
        Port("lg_mic_in", "IN", PortDirection.IN, PortGender.FEMALE, "eq_lg_mic", 1)
    )
    sys.add_port(
        Port("lg_mic_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_lg_mic", 1)
    )

    # StageBox Ch1 (Vo用)
    sys.add_port(
        Port("sb_in1", "Ch1 In", PortDirection.IN, PortGender.FEMALE, "eq_sb", 1)
    )
    sys.add_port(
        Port("sb_out1", "Ch1 Out", PortDirection.OUT, PortGender.MALE, "eq_sb", 1)
    )

    # StageBox Ch2 (Gt用)
    sys.add_port(
        Port("sb_in2", "Ch2 In", PortDirection.IN, PortGender.FEMALE, "eq_sb", 2)
    )
    sys.add_port(
        Port("sb_out2", "Ch2 Out", PortDirection.OUT, PortGender.MALE, "eq_sb", 2)
    )

    # ミキサー入力
    sys.add_port(
        Port("mix_in1", "Ch1 In", PortDirection.IN, PortGender.FEMALE, "eq_mix", 1)
    )
    sys.add_port(
        Port("mix_in2", "Ch2 In", PortDirection.IN, PortGender.FEMALE, "eq_mix", 2)
    )

    # テスト用のAux出力(オス) - 性別エラー検証用
    sys.add_port(
        Port("mix_aux1_out", "Aux1 Out", PortDirection.OUT, PortGender.MALE, "eq_mix")
    )

    return sys


def test_generate_model(patch_system):
    """PatchTableViewがequipment視点で動作するか確認"""
    PatchTableModel(patch_system, "eq_sb")


def test_get_model_column_length(patch_system):
    model = PatchTableModel(patch_system, "eq_sb")
    assert model.columnCount() == 6
