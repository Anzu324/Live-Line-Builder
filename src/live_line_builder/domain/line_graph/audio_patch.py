from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum

# ==========================================
# 1. データ定義 (Models)
# ==========================================


class NodeType(Enum):
    INSTRUMENT = "Instrument"
    MIC = "Microphone"
    STAGE_BOX = "StageBox"
    MIXER = "Mixer"
    PROCESSOR = "Processor"
    MAIN_AMP = "MainAmp"
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


# ==========================================
# 2. コアシステム (Logic)
# ==========================================


class AudioPatchSystem:
    """音響回線の状態管理とパッチング操作を提供するコアシステム"""

    def __init__(self):
        self.equipments: dict[str, Equipment] = {}
        self.ports: dict[str, Port] = {}

        # グラフ接続情報
        self.forward_edges: dict[str, set[str]] = {}  # OUT_port_id -> set(IN_port_ids)
        self.backward_edges: dict[str, str] = {}  # IN_port_id -> OUT_port_id

    # --- 単純な内部補助関数 ---
    def _get_equipment_id(self, port_id):
        return self.equipments[self.ports[port_id].equipment_id]

    # --- 登録・基本操作 ---

    def add_equipment(self, eq: Equipment):
        self.equipments[eq.id] = eq

    def add_port(self, port: Port):
        self.ports[port.id] = port
        if port.direction == PortDirection.OUT:
            # 出力側なら受け手のリストを作成
            self.forward_edges[port.id] = set()

    def connect_ports(self, port_a_id: str, port_b_id: str):
        """物理的な結線（方向は自動でOUT->INに正規化）"""
        p_a = self.ports[port_a_id]
        p_b = self.ports[port_b_id]

        if p_a.direction == p_b.direction:
            raise ValueError(f"同属性（{p_a.direction.value}同士）は接続できません。")

        out_port = p_a if p_a.direction == PortDirection.OUT else p_b
        in_port = p_b if p_a.direction == PortDirection.OUT else p_a

        # INポートの既存接続があれば上書き（古い線を抜く）
        if in_port.id in self.backward_edges:
            old_out = self.backward_edges[in_port.id]
            self.forward_edges[old_out].remove(in_port.id)

        self.forward_edges[out_port.id].add(in_port.id)
        self.backward_edges[in_port.id] = out_port.id

    def get_required_conversion(self, out_port_id: str, in_port_id: str) -> str | None:
        """物理的な整合性（オス/メス）を判定し、必要な変換を返す"""
        out_p = self.ports[out_port_id]
        in_p = self.ports[in_port_id]

        if out_p.gender == in_p.gender:
            return "要 M-M変換" if out_p.gender == PortGender.MALE else "要 F-F変換"
        return None

    # --- グラフ探索 (Generatorで分離) ---

    def _get_next_upstream_ports(self, port_id: str) -> list[str]:
        """指定ポートの1つ上流にあるポートID群を取得"""
        port = self.ports[port_id]
        if port.direction == PortDirection.IN:
            # INポートからは、結線されているOUTポートへ
            out_id = self.backward_edges.get(port_id)
            return [out_id] if out_id else []
        else:
            # OUTポートからは、同機器のINポートへ
            return [
                p.id
                for p in self.ports.values()
                if p.equipment_id == port.equipment_id
                and p.direction == PortDirection.IN
            ]

    def _traverse_upstream(self, start_port_id: str) -> Iterator[str]:
        """ポートから上流へ向かってノードを巡回するジェネレータ"""
        visited = set()
        stack = [start_port_id]
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            yield curr
            stack.extend(self._get_next_upstream_ports(curr))

    def _get_next_downstream_ports(self, port_id: str) -> list[str]:
        """指定ポートの1つ下流にあるポートID群を取得"""
        port = self.ports[port_id]
        if port.direction == PortDirection.OUT:
            # OUTポートからは、結線されているINポート群へ
            return list(self.forward_edges.get(port_id, []))
        else:
            # INポートからは、同機器の同Ch OUTポートへ
            return [
                p.id
                for p in self.ports.values()
                if p.equipment_id == port.equipment_id
                and p.direction == PortDirection.OUT
                and p.channel_no == port.channel_no
            ]

    def _traverse_downstream(self, start_port_id: str) -> Iterator[str]:
        """ポートから下流へ向かってノードを巡回するジェネレータ"""
        visited = set()
        stack = [start_port_id]
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            yield curr
            stack.extend(self._get_next_downstream_ports(curr))

    # --- 高度な自動パッチング機能 ---

    def auto_patch_mixer_from_stagebox(
        self, mixer_in_port_id: str, stagebox_eq_id: str, ch_no: int
    ) -> Equipment | None:
        """マルチの番号を指定してミキサーに繋ぐ。成功した場合、上流の楽器を返す。"""
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
            raise ValueError(
                f"指定されたStageBox(Ch.{ch_no})の出力ポートが見つかりません。"
            )

        self.connect_ports(sb_out_port.id, mixer_in_port_id)

        # 上流を探索して楽器を特定する
        for port_id in self._traverse_upstream(sb_out_port.id):
            eq = self.equipments[self.ports[port_id].equipment_id]
            if eq.type in (NodeType.INSTRUMENT, NodeType.MIC):
                return eq
        return None

    def auto_patch_mixer_from_instrument(
        self, mixer_in_port_id: str, instrument_eq_id: str
    ) -> Port:
        """楽器を指定し、マルチを経由してミキサーに繋ぐ。成功した場合、経由したマルチのポートを返す。"""
        out_ports = [
            p
            for p in self.ports.values()
            if p.equipment_id == instrument_eq_id and p.direction == PortDirection.OUT
        ]
        if not out_ports:
            raise ValueError("指定された楽器に出力ポートが存在しません。")

        # 下流を探索してマルチのOUTを探す
        sb_out_port = None
        for port_id in self._traverse_downstream(out_ports[0].id):
            port = self.ports[port_id]
            eq = self.equipments[port.equipment_id]
            if eq.type == NodeType.STAGE_BOX and port.direction == PortDirection.OUT:
                sb_out_port = port
                break

        if not sb_out_port:
            raise ValueError("この楽器はStageBoxまで回線が到達していません。")

        self.connect_ports(sb_out_port.id, mixer_in_port_id)
        return sb_out_port

    # 長さ取得系関数
    def get_upstream_length(self, start_port_id: str) -> int:
        visited = set()
        # 開始ポートの深さを 1 に設定
        stack = [(start_port_id, 1)]
        max_length = 0

        while stack:
            curr_id, current_depth = stack.pop()

            if curr_id in visited:
                continue
            visited.add(curr_id)

            # 探索した深さがこれまでの最大値を超えたら上書き更新
            max_length = max(max_length, current_depth)

            # 上流ノードを取得し、深さを +1 してスタックに追加
            upstream_ports = self._get_next_upstream_ports(curr_id)
            stack.extend([(port_id, current_depth + 1) for port_id in upstream_ports])

        return max_length

    def get_downstream_length(self, start_port_id: str) -> int:
        # スタックには (現在のポートID, 現在の深さ, 現在の経路のセット) を入れる
        stack = [(start_port_id, 0, {start_port_id})]
        max_length = 0

        while stack:
            curr_id, current_depth, current_path = stack.pop()

            max_length = max(max_length, current_depth)

            # 下流ポートを取得（スプリットにより複数ポートが返る想定）
            downstream_ports = self._get_next_downstream_ports(curr_id)

            for next_port in downstream_ports:
                # 【重要】現在のルート内で既に通ったポートに再度到達したか（ループ検知）
                if next_port in current_path:
                    # 無限ループ（ハウリングの原因など）を防ぐため、このルートの探索は打ち切る
                    # 必要に応じてここでログを出したり、例外を投げることも可能
                    continue

                # 現在のルート情報をコピーし、次のポートを加えてスタックに積む
                new_path = current_path.copy()
                new_path.add(next_port)
                stack.append((next_port, current_depth + 1, new_path))

        return max_length

    def get_downstream_equipment_length(self, start_port_id: str) -> int:

        # スタック: (現在のポートID, 経由した機材数, ループ検知用の通過済みポートセット)
        # 開始時点で1台目の機材内にいるため、機材数は 1 とする
        stack = [(start_port_id, 1, {start_port_id})]
        max_eq_length = 0

        while stack:
            curr_port_id, current_eq_count, current_path = stack.pop()
            curr_eq_id = self._get_equipment_id(curr_port_id)

            # 最大機材経由数を更新
            max_eq_length = max(max_eq_length, current_eq_count)

            # 下流ポートを取得（ケーブルでの外部接続、または機材内部のルーティング）
            downstream_ports = self._get_next_downstream_ports(curr_port_id)

            for next_port_id in downstream_ports:
                # 【重要】ループ検知は「機材」ではなく「ポート」単位で行う
                if next_port_id in current_path:
                    continue

                next_eq_id = self._get_equipment_id(next_port_id)

                # 2. 所属する機材が変わった場合のみ、カウントを増やす
                next_eq_count = current_eq_count
                if next_eq_id != curr_eq_id:
                    next_eq_count += 1

                new_path = current_path.copy()
                new_path.add(next_port_id)
                stack.append((next_port_id, next_eq_count, new_path))

        return max_eq_length


# ==========================================
# 3. 表示専用関数 (Output & Visualization)
# ==========================================


def print_visual_patch_flow(sys: AudioPatchSystem):
    """【表示機能 1】横並びで回線のフローをビジュアル表示する"""
    print("\n=== ビジュアル回線フロー ===")

    def build_chain(out_id: str, in_id: str) -> str:
        out_p = sys.ports[out_id]
        in_p = sys.ports[in_id]
        out_eq = sys.equipments[out_p.equipment_id]
        in_eq = sys.equipments[in_p.equipment_id]

        conv = sys.get_required_conversion(out_id, in_id)
        arrow = f" --[{conv}]--> " if conv else " ----> "
        chain_str = f"[{out_eq.name}:{out_p.name}]{arrow}[{in_eq.name}:{in_p.name}]"

        # 下流ポートがあれば再帰的に繋ぐ
        for next_out_id in sys._get_next_downstream_ports(in_id):
            for next_in_id in sys.forward_edges.get(next_out_id, []):
                chain_str += "\n      └─ " + build_chain(next_out_id, next_in_id)
        return chain_str

    is_empty = True
    for out_id, in_ids in sys.forward_edges.items():
        # 【修正点】同機器内に上流INポートを持たないOUTポート（＝マイク・楽器など最上流）を起点にする
        if not sys._get_next_upstream_ports(out_id):
            for in_id in in_ids:
                print(build_chain(out_id, in_id))
                is_empty = False

    if is_empty:
        print("結線がありません。")


def print_all_connections(sys: AudioPatchSystem):
    """【表示機能 2】全てのパッチ（結線）リストを列挙表示する"""
    print("\n=== 現在のパッチリスト ===")
    for out_id, in_ids in sys.forward_edges.items():
        out_p = sys.ports[out_id]
        out_eq = sys.equipments[out_p.equipment_id]

        for in_id in in_ids:
            in_p = sys.ports[in_id]
            in_eq = sys.equipments[in_p.equipment_id]
            print(
                f"OUT: {out_eq.name} ({out_p.name}) => IN: {in_eq.name} ({in_p.name})"
            )


# ==========================================
# 4. テスト用シナリオ (AI・開発者向け)
# ==========================================
if __name__ == "__main__":
    """
    【テスト設計ヒント】
    別のAIが pytest などを作成する場合、以下の Arrange (準備), Act (実行), Assert (検証) の
    流れを参考にテストケースを構築してください。
    - 正常系: 返り値のオブジェクトのアサーション (assert result.name == "...")
    - 異常系: 例外が正しく発生するかの検証 (with pytest.raises(ValueError): ...)
    """
    sys = AudioPatchSystem()

    # --- [Arrange] 事前データの準備 ---
    sys.add_equipment(Equipment("eq_vo", "Vo.Mic", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_gt", "Gt.Amp", NodeType.INSTRUMENT))
    sys.add_equipment(Equipment("eq_sb", "StageBox16", NodeType.STAGE_BOX))
    sys.add_equipment(Equipment("eq_mix", "CL5 Console", NodeType.MIXER))

    sys.add_port(Port("vo_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_vo"))
    sys.add_port(Port("gt_out", "Out", PortDirection.OUT, PortGender.MALE, "eq_gt"))

    # StageBox Ch1 (Vo用)
    sys.add_port(
        Port("sb_in1", "Ch1 In", PortDirection.IN, PortGender.FEMALE, "eq_sb", 1)
    )
    sys.add_port(
        Port("sb_out1", "Ch1 Out", PortDirection.OUT, PortGender.MALE, "eq_sb", 1)
    )
    # StageBox Ch2 (Gt用, まだ結線されていない)
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

    # 舞台上の仕込み配線 (Vo -> マルチCh1)
    sys.connect_ports("vo_out", "sb_in1")

    # --- [Act & Assert] テストケースの実行 ---

    print("--- 正常系テスト1: マルチ指定でのパッチング ---")
    # 期待値: Ch1を指定すると、結線が成功し、上流の「Vo.Mic」が返されること。
    found_inst = sys.auto_patch_mixer_from_stagebox(
        mixer_in_port_id="mix_in1", stagebox_eq_id="eq_sb", ch_no=1
    )
    if found_inst:
        print(f"成功: 自動結線完了。検出された楽器 -> {found_inst.name}")

    print("\n--- 異常系テスト1: 未配線の楽器を指定した場合 ---")
    # 期待値: Gt.Ampはまだマルチに繋がっていないため、ValueErrorが起きること。
    try:
        sys.auto_patch_mixer_from_instrument(
            mixer_in_port_id="mix_in2", instrument_eq_id="eq_gt"
        )
    except ValueError as e:
        print(f"想定通りのエラー発生: {e}")

    print("\n--- 異常系テスト2: 性別エラー(変換プラグ必要)の検証 ---")
    # 期待値: オス同士を繋ごうとした場合、get_required_conversion で "要 M-M変換" が返ること。

    sys.add_port(
        Port("mix_aux1_out", "Aux1 Out", PortDirection.OUT, PortGender.MALE, "eq_mix")
    )
    try:
        # (注意: connect_ports自体は論理結線なので実行可能。表示時に物理警告が出る設計)
        sys.connect_ports("mix_aux1_out", "sb_out2")
    except ValueError as e:
        print(f"想定通りのエラー発生: {e}")

    # --- 出力機能のテスト ---
    print_all_connections(sys)
    print_visual_patch_flow(sys)
