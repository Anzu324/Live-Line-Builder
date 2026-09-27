import pytest

from graph.const import *
from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    DuplicateIDError,
    EquipmentCategory,
    EquipmentDTO,
    EquipmentInstance,
    InvalidConnectionError,
    PortDirection,
    PortGender,
    PortInstance,
    PortNotFoundError,
)


@pytest.fixture
def patch_system():
    """各テストで共通して使用する初期状態のシステム(Fixture)"""
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

    # 楽器・マイクポート
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
            MIX_AUX1_OUT,
            "Aux1 Out",
            PortDirection.OUT,
            PortGender.MALE,
            EQ_MIX,
        )
    )

    # 機材内部の配線設定 (IN -> OUT への内部経路)
    # LG_MIC: IN -> OUT
    sys.forward_edges.setdefault(LG_MIC_IN, set()).add(LG_MIC_OUT)
    sys.backward_edges[LG_MIC_OUT] = LG_MIC_IN

    # StageBox Ch1: IN1 -> OUT1
    sys.forward_edges.setdefault(SB_IN1, set()).add(SB_OUT1)
    sys.backward_edges[SB_OUT1] = SB_IN1

    # StageBox Ch2: IN2 -> OUT2
    sys.forward_edges.setdefault(SB_IN2, set()).add(SB_OUT2)
    sys.backward_edges[SB_OUT2] = SB_IN2

    return sys


# ==========================================
# 基本操作のテスト
# ==========================================


def test_add_equipment_and_port(patch_system):
    """機器とポートが正しく登録されるか"""
    assert EQ_VO in patch_system.equipments
    assert VO_OUT in patch_system.ports
    assert patch_system.ports[VO_OUT].direction == PortDirection.OUT
    assert VO_OUT in patch_system.forward_edges


def test_add_equipment_dto_duplicate_error(patch_system):
    """重複したポートIDを持つEquipmentDTOを追加した際、DuplicateIDErrorが発生するか"""
    duplicate_dto = EquipmentDTO(
        equipment=EquipmentInstance(
            EquipmentID("eq_dup"), "Duplicate", EquipmentCategory.MIC
        ),
        ports={
            VO_OUT: PortInstance(
                VO_OUT,
                "DupOut",
                PortDirection.OUT,
                PortGender.MALE,
                EquipmentID("eq_dup"),
            )
        },
        downstream_edges={},
        upstream_edges={},
    )
    with pytest.raises(DuplicateIDError):
        patch_system.add_equipment(duplicate_dto)


def test_connect_ports_success(patch_system):
    """正常にポート同士が結線されるか"""
    patch_system.connect_ports(VO_OUT, SB_IN1)

    # 順方向(OUT -> IN)の確認
    assert SB_IN1 in patch_system.forward_edges[VO_OUT]
    # 逆方向(IN -> OUT)の確認
    assert patch_system.backward_edges[SB_IN1] == VO_OUT


def test_connect_ports_not_found_error(patch_system):
    """存在しないポートを指定した際に PortNotFoundError が発生するか"""
    with pytest.raises(PortNotFoundError):
        patch_system.connect_ports(PortID("invalid_out"), SB_IN1)

    with pytest.raises(PortNotFoundError):
        patch_system.connect_ports(VO_OUT, PortID("invalid_in"))


def test_connect_ports_same_direction_error(patch_system):
    """同属性（OUT同士、IN同士）の接続で InvalidConnectionError が発生するか"""
    # OUT同士
    with pytest.raises(
        InvalidConnectionError, match="同属性（OUT同士）のポートは接続できません"
    ):
        patch_system.connect_ports(VO_OUT, LG_OUT)

    # IN同士
    with pytest.raises(
        InvalidConnectionError, match="同属性（IN同士）のポートは接続できません"
    ):
        patch_system.connect_ports(SB_IN1, SB_IN2)


def test_connect_ports_overwrite_existing(patch_system):
    """すでに結線されているINポートに別のOUTを繋いだ場合、上書きされるか"""
    # 初期接続 (Vo -> StageBox Ch1)
    patch_system.connect_ports(VO_OUT, SB_IN1)
    assert SB_IN1 in patch_system.forward_edges[VO_OUT]

    # 別の出力(Gt)を同じ入力(StageBox Ch1)に接続
    patch_system.connect_ports(LG_OUT, SB_IN1)

    # 古い結線(Vo)から削除されていること
    assert SB_IN1 not in patch_system.forward_edges[VO_OUT]
    # 新しい結線(Gt)が登録されていること
    assert SB_IN1 in patch_system.forward_edges[LG_OUT]
    assert patch_system.backward_edges[SB_IN1] == LG_OUT


def test_get_required_conversion(patch_system):
    """物理的整合性（オス/メス）の判定と変換プラグの必要性が正しいか"""
    # 正常（MALE -> FEMALE）
    assert patch_system.get_required_conversion(VO_OUT, SB_IN1) is None

    # 異常: MALE -> MALE
    assert patch_system.get_required_conversion(MIX_AUX1_OUT, SB_OUT2) == "要 M-M変換"


# ==========================================
# 探索・長さ計算機能のテスト
# ==========================================


def test_get_upstream_port_count(patch_system):
    """入力側へたどった時の最深ポートまでのノード数を計算"""
    # 1. Vo.Mic -> StageBox Ch1 -> Mixer Ch1 の経路 (長さ: 4)
    patch_system.connect_ports(VO_OUT, SB_IN1)
    patch_system.connect_ports(SB_OUT1, MIX_IN1)
    assert patch_system.get_upstream_port_count(MIX_IN1) == 4
    # 経路: MIX_IN1(1) -> SB_OUT1(2) -> SB_IN1(3) -> VO_OUT(4)

    # 2. LG.Amp -> LG.Mic -> StageBox Ch2 -> Mixer Ch2 の経路 (長さ: 6)
    patch_system.connect_ports(LG_OUT, LG_MIC_IN)
    patch_system.connect_ports(LG_MIC_OUT, SB_IN2)
    patch_system.connect_ports(SB_OUT2, MIX_IN2)
    assert patch_system.get_upstream_port_count(MIX_IN2) == 6
    # 経路: MIX_IN2(1) -> SB_OUT2(2) -> SB_IN2(3) -> LG_MIC_OUT(4) -> LG_MIC_IN(5) -> LG_OUT(6)


def test_get_upstream_ports(patch_system):
    """指定ポートから上流に辿れるポートリストを取得できるか"""
    patch_system.connect_ports(VO_OUT, SB_IN1)
    patch_system.connect_ports(SB_OUT1, MIX_IN1)

    upstream_list = patch_system.get_upstream_ports(MIX_IN1)

    # 起点から順に上流へ辿ったリストになっているか確認
    assert upstream_list == [MIX_IN1, SB_OUT1, SB_IN1, VO_OUT]


def test_get_downstream_equipment_length(patch_system):
    """通過する機材の台数を正しくカウントできるか"""
    patch_system.connect_ports(VO_OUT, SB_IN1)
    patch_system.connect_ports(SB_OUT1, MIX_IN1)

    # VO_OUT 起点で下流へ向かうと Vo.Mic(1) -> StageBox(2) -> Mixer(3) で計 3 台
    eq_count = patch_system.get_downstream_equipment_length(VO_OUT)
    assert eq_count == 3
