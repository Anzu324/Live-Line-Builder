import pytest

from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    Equipment,
    NodeType,
    Port,
    PortDirection,
    PortGender,
)


@pytest.fixture
def patch_system():
    """
    各テストで共通して使用する初期状態のシステム(Fixture)
    元のコードのヒント「4. テスト用シナリオ」に沿ったデータを準備します。
    """
    sys = AudioPatchSystem()

    # --- [Arrange] 事前データの準備 ---
    sys.add_equipment(Equipment("eq_vo", "Vo.Mic", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_gt", "Gt.Amp", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_sb", "StageBox16", NodeType.STAGE_BOX))
    sys.add_equipment(Equipment("eq_mix", "MG24/14FX Console", NodeType.MIXER))

    # 楽器出力ポート
    sys.add_port(Port("vo_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_vo"))
    sys.add_port(Port("gt_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_gt"))

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


# ==========================================
# 基本操作のテスト
# ==========================================


def test_add_equipment_and_port(patch_system):
    """機器とポートが正しく登録されるか"""
    assert "eq_vo" in patch_system.equipments
    assert "vo_out" in patch_system.ports
    assert patch_system.ports["vo_out"].direction == PortDirection.OUT
    assert "vo_out" in patch_system.forward_edges


def test_connect_ports_success(patch_system):
    """正常にポート同士が結線されるか"""
    patch_system.connect_ports("vo_out", "sb_in1")

    # 順方向(OUT -> IN)の確認
    assert "sb_in1" in patch_system.forward_edges["vo_out"]
    # 逆方向(IN -> OUT)の確認
    assert patch_system.backward_edges["sb_in1"] == "vo_out"


def test_connect_ports_same_direction_error(patch_system):
    """同属性（OUT同士、IN同士）の接続でエラーが発生するか"""
    # OUT同士
    with pytest.raises(ValueError, match="同属性（OUT同士）は接続できません。"):
        patch_system.connect_ports("vo_out", "gt_out")

    # IN同士
    with pytest.raises(ValueError, match="同属性（IN同士）は接続できません。"):
        patch_system.connect_ports("sb_in1", "sb_in2")


def test_connect_ports_overwrite_existing(patch_system):
    """すでに結線されているINポートに別のOUTを繋いだ場合、上書きされるか"""
    # 初期接続 (Vo -> StageBox Ch1)
    patch_system.connect_ports("vo_out", "sb_in1")
    assert "sb_in1" in patch_system.forward_edges["vo_out"]

    # 別の出力(Gt)を同じ入力(StageBox Ch1)に接続
    patch_system.connect_ports("gt_out", "sb_in1")

    # 古い結線(Vo)から削除されていること
    assert "sb_in1" not in patch_system.forward_edges["vo_out"]
    # 新しい結線(Gt)が登録されていること
    assert "sb_in1" in patch_system.forward_edges["gt_out"]
    assert patch_system.backward_edges["sb_in1"] == "gt_out"


def test_get_required_conversion(patch_system):
    """物理的整合性（オス/メス）の判定と変換プラグの必要性が正しいか"""
    # 正常（MALE -> FEMALE）
    assert patch_system.get_required_conversion("vo_out", "sb_in1") is None

    # 異常: MALE -> MALE (例: ミキサーAUXからStageBoxのOUTに繋ぐような誤配線チェック)
    assert (
        patch_system.get_required_conversion("mix_aux1_out", "sb_out2") == "要 M-M変換"
    )


# ==========================================
# 自動パッチング (高度な機能) のテスト
# ==========================================


def test_auto_patch_mixer_from_stagebox_success(patch_system):
    """【正常系1】StageBoxのCh指定による自動パッチングが成功するか"""
    # [Arrange] 舞台上の仕込み配線 (Vo -> マルチCh1)
    patch_system.connect_ports("vo_out", "sb_in1")

    # [Act] ミキサーのCh1にマルチのCh1をパッチング
    found_inst = patch_system.auto_patch_mixer_from_stagebox(
        mixer_in_port_id="mix_in1", stagebox_eq_id="eq_sb", ch_no=1
    )

    # [Assert] 結線が完了し、上流のVo.Micが返却されること
    assert found_inst is not None
    assert found_inst.id == "eq_vo"
    assert found_inst.name == "Vo.Mic"
    # ミキサー入力側に正しく繋がっているか
    assert "mix_in1" in patch_system.forward_edges["sb_out1"]


def test_auto_patch_mixer_from_stagebox_not_found(patch_system):
    """【異常系】存在しないCh番号を指定した場合のエラー"""
    with pytest.raises(
        ValueError, match=r"指定されたStageBox\(Ch.99\)の出力ポートが見つかりません。"
    ):
        patch_system.auto_patch_mixer_from_stagebox(
            mixer_in_port_id="mix_in1", stagebox_eq_id="eq_sb", ch_no=99
        )


def test_auto_patch_mixer_from_instrument_success(patch_system):
    """【正常系2】楽器指定による自動パッチングが成功するか"""
    # [Arrange] 舞台上の仕込み配線 (Gt -> マルチCh2)
    patch_system.connect_ports("gt_out", "sb_in2")

    # [Act] 楽器(Gt)を指定してミキサーにパッチング
    sb_out_port = patch_system.auto_patch_mixer_from_instrument(
        mixer_in_port_id="mix_in2", instrument_eq_id="eq_gt"
    )

    # [Assert] 経由したStageBoxの出力ポートが返却され、結線が完了していること
    assert sb_out_port is not None
    assert sb_out_port.id == "sb_out2"
    assert "mix_in2" in patch_system.forward_edges["sb_out2"]


def test_auto_patch_mixer_from_instrument_not_connected(patch_system):
    """【異常系1】StageBoxに未配線の楽器を指定した場合のエラー"""
    # Gt.Ampはどこにも繋がっていない状態
    with pytest.raises(
        ValueError, match="この楽器はStageBoxまで回線が到達していません。"
    ):
        patch_system.auto_patch_mixer_from_instrument(
            mixer_in_port_id="mix_in2", instrument_eq_id="eq_gt"
        )


def test_auto_patch_mixer_from_instrument_no_out_ports(patch_system):
    """【異常系】出力ポートを持たない楽器を指定した場合のエラー"""
    # 出力ポートを持たないダミー楽器を追加
    patch_system.add_equipment(Equipment("eq_dummy", "Dummy", NodeType.INSTRUMENT))

    with pytest.raises(ValueError, match="指定された楽器に出力ポートが存在しません。"):
        patch_system.auto_patch_mixer_from_instrument(
            mixer_in_port_id="mix_in2", instrument_eq_id="eq_dummy"
        )
