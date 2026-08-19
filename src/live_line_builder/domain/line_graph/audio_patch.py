import json
from dataclasses import asdict, dataclass
from enum import Enum

# AIが出力したものを一部コメントしたままそのまま貼り付けています。
# TODO:テストを作成。複雑なシステムです。検証必須。
# TODO:その他のシステムとの整合性をとって組み込む。


# 機材の種類を表す。ポートの計算の流れの挙動を制御する。
class NodeType(Enum):
    INSTRUMENT = "Instrument"
    MIC = "Mic"
    STAGE_BOX = "StageBox"
    MIXER = "Mixer"
    PROCESSOR = "Processor"
    MAIN_AMP = "Amplifier"
    SPEAKER = "Speaker"


# ポートの方向
class PortDirection(Enum):
    OUT = "OUT"
    IN = "IN"


# ポートの物理的形状を示す
class PortGender(Enum):
    MALE = "Male"
    FEMALE = "Female"


@dataclass
class Port:
    id: str
    name: str
    direction: PortDirection
    gender: PortGender
    equipment_id: str
    channel_no: int | None = None


@dataclass
class Equipment:
    id: str
    name: str
    type: NodeType


class AudioPatchSystem:
    def __init__(self):
        self.equipments: dict[str, Equipment] = {}
        self.ports: dict[str, Port] = {}
        self.forward_edges: dict[str, set[str]] = {}  # OUT -> set(IN)
        self.backward_edges: dict[str, str] = {}  # IN -> OUT (1対1制御)

    def add_equipment(self, eq: Equipment):
        self.equipments[eq.id] = eq

    def add_port(self, port: Port):
        self.ports[port.id] = port
        if port.direction == PortDirection.OUT:
            # 出力側なら受け手のリストを作成
            self.forward_edges[port.id] = set()

    def connect_ports(self, port_a_id: str, port_b_id: str):
        """方向を自動正規化（OUT -> IN）してパッチング（INの上書き制御含む）"""
        p_a = self.ports[port_a_id]
        p_b = self.ports[port_b_id]

        if p_a.direction == p_b.direction:
            raise ValueError(f"同属性（{p_a.direction.value}同士）は接続できません")

        out_port = p_a if p_a.direction == PortDirection.OUT else p_b
        in_port = p_b if p_a.direction == PortDirection.OUT else p_a

        # INポートの既存接続を上書き解除
        if in_port.id in self.backward_edges:
            old_out = self.backward_edges[in_port.id]
            self.forward_edges[old_out].remove(in_port.id)

        self.forward_edges[out_port.id].add(in_port.id)
        self.backward_edges[in_port.id] = out_port.id

    def check_conversion_needed(self, out_port_id: str, in_port_id: str) -> str | None:
        """オス/メスの物理的整合性を判定し、必要な変換ケーブルを返す"""
        out_p = self.ports[out_port_id]
        in_p = self.ports[in_port_id]
        if out_p.gender == in_p.gender:
            return "[要 F-F変換]" if out_p.gender == PortGender.MALE else "[要 M-M変換]"
        return None

    # --- アサイン機能 ---

    def assign_by_stagebox(
        self, mixer_in_port_id: str, stagebox_eq_id: str, ch_no: int
    ):
        """マルチ番号指定 -> 接続＆上流の楽器を自動割り出し"""
        sb_out_port = next(
            (
                p
                for p in self.ports.values()
                if p.equipment_id == stagebox_eq_id
                and p.channel_no == ch_no
                and p.direction == PortDirection.OUT
            ),
            None,
        )
        if not sb_out_port:
            return

        self.connect_ports(sb_out_port.id, mixer_in_port_id)
        inst = self._find_upstream_instrument(sb_out_port.id)
        inst_name = inst.name if inst else "（音源なし）"
        print(f"マルチCh.{ch_no} -> ミキサー割り当て（検出楽器: {inst_name}）")

    def assign_by_instrument(self, mixer_in_port_id: str, instrument_eq_id: str):
        """楽器指定 -> マルチ接続確認＆自動パッチング"""
        sb_out_port = self._find_downstream_stagebox_out(instrument_eq_id)
        if not sb_out_port:
            print("マルチまで回線が到達していません")
            return

        self.connect_ports(sb_out_port.id, mixer_in_port_id)
        inst_name = self.equipments[instrument_eq_id].name
        print(
            f"{inst_name}（マルチCh.{sb_out_port.channel_no}経由）-> ミキサーに自動アサイン"
        )

    # --- 探索ロジック ---

    def _find_upstream_instrument(self, start_port_id: str) -> Equipment | None:
        curr_id = start_port_id
        visited = set()
        while curr_id and curr_id not in visited:
            visited.add(curr_id)
            port = self.ports[curr_id]
            eq = self.equipments[port.equipment_id]
            if eq.type in (NodeType.INSTRUMENT, NodeType.MIC):
                return eq

            if port.direction == PortDirection.IN:
                curr_id = self.backward_edges.get(curr_id)
            else:
                in_ports = [
                    p
                    for p in self.ports.values()
                    if p.equipment_id == port.equipment_id
                    and p.direction == PortDirection.IN
                ]
                curr_id = in_ports[0].id if in_ports else None
        return None

    def _find_downstream_stagebox_out(self, instrument_eq_id: str) -> Port | None:
        out_ports = [
            p
            for p in self.ports.values()
            if p.equipment_id == instrument_eq_id and p.direction == PortDirection.OUT
        ]
        if not out_ports:
            return None

        stack = [out_ports[0].id]
        visited = set()
        while stack:
            curr_id = stack.pop()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            port = self.ports[curr_id]
            eq = self.equipments[port.equipment_id]

            if eq.type == NodeType.STAGE_BOX and port.direction == PortDirection.OUT:
                return port

            if port.direction == PortDirection.OUT:
                stack.extend(self.forward_edges.get(curr_id, []))
            else:
                same_ch_outs = [
                    p.id
                    for p in self.ports.values()
                    if p.equipment_id == port.equipment_id
                    and p.direction == PortDirection.OUT
                    and p.channel_no == port.channel_no
                ]
                stack.extend(same_ch_outs)
        return None

    # --- 表示・保存 ---

    def render_patch_sheet(self):
        """舞台用：横並び回線フロー表示（変換ケーブル注記付き）"""
        print("\n=== 音響回線表 ===")
        # 各全OUTポートから開始するフローを表示
        processed_starts = set()
        for out_id, in_ids in self.forward_edges.items():
            if out_id in self.backward_edges.values():
                continue  # 途中のノードはスキップ

            for in_id in in_ids:
                chain_str = self._build_chain_string(out_id, in_id)
                print(chain_str)

    def _build_chain_string(self, out_id: str, in_id: str) -> str:
        out_p = self.ports[out_id]
        in_p = self.ports[in_id]
        out_eq = self.equipments[out_p.equipment_id]
        in_eq = self.equipments[in_p.equipment_id]

        conv = self.check_conversion_needed(out_id, in_id)
        arrow = f" =={conv}==> " if conv else " ==> "

        res = f"[{out_eq.name}:{out_p.name}]{arrow}[{in_eq.name}:{in_p.name}]"

        # さらに下流へ続く場合
        next_out_ports = [
            p
            for p in self.ports.values()
            if p.equipment_id == in_p.equipment_id
            and p.direction == PortDirection.OUT
            and p.channel_no == in_p.channel_no
        ]
        for next_out in next_out_ports:
            for next_in_id in self.forward_edges.get(next_out.id, []):
                res += " ==> " + self._build_chain_string(next_out.id, next_in_id)
        return res

    def save_to_file(self, filepath: str):
        data = {
            "equipments": [asdict(e) for e in self.equipments.values()],
            "ports": [
                {
                    **asdict(p),
                    "direction": p.direction.value,
                    "gender": p.gender.value,
                }
                for p in self.ports.values()
            ],
            "connections": [
                {"from": u, "to": v}
                for u, targets in self.forward_edges.items()
                for v in targets
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# --- 動作確認 ---
if __name__ == "__main__":
    sys = AudioPatchSystem()

    # 機材・ポート登録
    sys.add_equipment(Equipment("eq_vo", "Vo.Mic", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_sb", "StageBox16", NodeType.STAGE_BOX))
    sys.add_equipment(Equipment("eq_mix", "CL5 Console", NodeType.MIXER))

    # 入力系統ポート (通常オス->メス)
    sys.add_port(
        Port(
            "vo_out",
            "Out",
            PortDirection.OUT,
            PortGender.MALE,
            "eq_vo",
        )
    )
    sys.add_port(
        Port(
            "sb_in1",
            "Ch1 In",
            PortDirection.IN,
            PortGender.FEMALE,
            "eq_sb",
            channel_no=1,
        )
    )
    sys.add_port(
        Port(
            "sb_out1",
            "Ch1 Out",
            PortDirection.OUT,
            PortGender.MALE,
            "eq_sb",
            channel_no=1,
        )
    )
    sys.add_port(
        Port(
            "mix_in1",
            "Ch1 In",
            PortDirection.IN,
            PortGender.FEMALE,
            "eq_mix",
            channel_no=1,
        )
    )

    # 1. 舞台配線 (Vo -> マルチCh1)
    sys.connect_ports("vo_out", "sb_in1")

    # 2. モードA（マルチ指定で卓にアサイン）
    sys.assign_by_stagebox("mix_in1", "eq_sb", ch_no=1)

    # 3. 横並び表示（変換なし）
    sys.render_patch_sheet()

    # 4. イレギュラー例：卓Aux Out (Male) -> マルチ舞台側Ch16 (Female: 現場で逆に使うケース)
    sys.add_port(
        Port(
            "mix_aux1",
            "Aux1 Out",
            PortDirection.OUT,
            PortGender.MALE,
            "eq_mix",
        )
    )
    sys.add_port(
        Port(
            "sb_in16",
            "Ch16 In(Stage)",
            PortDirection.IN,
            PortGender.FEMALE,
            "eq_sb",
            channel_no=16,
        )
    )

    sys.connect_ports("mix_aux1", "sb_in16")

    # 変換コードが必要な回線表示
    sys.render_patch_sheet()
