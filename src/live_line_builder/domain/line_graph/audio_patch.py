from collections.abc import Collection, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import NewType

# ==========================================
# 1. データ定義 & カスタム例外 (Models & Exceptions)
# ==========================================

EquipmentID = NewType("EquipmentID", str)
PortID = NewType("PortID", str)


class EquipmentCategory(Enum):
    INSTRUMENT = "Instrument"
    MIC = "Microphone"
    MULTI_BOX = "MultiBox"
    MIXER = "Mixer"
    PROCESSOR = "Processor"
    POWER_AMP = "PowerAmp"
    SPEAKER = "Speaker"


# ポートの方向
class PortDirection(Enum):
    OUT = "OUT"
    IN = "IN"


# ポートの物理的形状を示す
class PortGender(Enum):
    MALE = "Male"
    FEMALE = "Female"


# --- カスタム例外定義 ---


class AudioPatchError(Exception):
    """音響パッチシステム全般の基底例外クラス"""


class InvalidConnectionError(AudioPatchError):
    """同属性（IN同士/OUT同士）など、不適切なポート接続が行われた際のエラー"""

    def __init__(
        self, port_a_id: PortID, port_b_id: PortID, direction: PortDirection
    ) -> None:
        self.port_a_id = port_a_id
        self.port_b_id = port_b_id
        self.direction = direction
        super().__init__(
            f"同属性（{direction.value}同士）のポートは接続できません: "
            f"'{port_a_id}' <-> '{port_b_id}'"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"port_a_id={self.port_a_id!r}, port_b_id={self.port_b_id!r}, direction={self.direction!r})"
        )


class DuplicateIDError(AudioPatchError):
    """IDの重複が検知された際のエラー"""

    def __init__(self, duplicate_ids: Collection[PortID | EquipmentID]) -> None:
        # 内部で set に変換して保持することで、渡されたコレクション型に柔軟に対応します
        self.duplicate_ids = set(duplicate_ids)
        super().__init__(f"IDの重複が検知されました: {', '.join(duplicate_ids)}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(duplicate_ids={self.duplicate_ids!r})"


class PortNotFoundError(AudioPatchError):
    """指定されたポートが存在しない際のエラー"""

    def __init__(self, port_id: PortID, context_msg: str = "") -> None:
        self.port_id = port_id
        msg = f"ポート '{port_id}' が見つかりません。"
        if context_msg:
            msg += f" ({context_msg})"
        super().__init__(msg)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(port_id={self.port_id!r})"


class RouteNotFoundError(AudioPatchError):
    """回線が目的地まで到達していない・接続されていない際のエラー"""

    def __init__(self, start_id: PortID | EquipmentID, target_type: str) -> None:
        self.start_id = start_id
        self.target_type = target_type
        super().__init__(
            f"'{start_id}' から '{target_type}' までの回線が到達していません。"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(start_id={self.start_id!r}, target_type={self.target_type!r})"


# --- データエンティティ ---


@dataclass
class PortInstance:
    id: PortID
    name: str
    direction: PortDirection
    gender: PortGender
    equipment_id: EquipmentID
    channel_no: int | None = None


@dataclass
class EquipmentInstance:
    id: EquipmentID
    name: str
    type: EquipmentCategory


@dataclass
class EquipmentDTO:
    """アダプターからメインシステムに追加するオブジェクト情報を伝播するためのオブジェクトです。

    IDはUUIDの生成機を用いてください。
    """

    equipment: EquipmentInstance
    ports: dict[PortID, PortInstance]
    downstream_edges: dict[PortID, set[PortID]]
    upstream_edges: dict[PortID, PortID]


# ==========================================
# 2. コアシステム (Logic)
# ==========================================


class AudioPatchSystem:
    """音響回線の状態管理とパッチング操作を提供するコアシステム"""

    def __init__(self) -> None:
        self.equipments: dict[EquipmentID, EquipmentInstance] = {}
        self.ports: dict[PortID, PortInstance] = {}

        # グラフ接続情報（外部結線および機材内部配線を含む）
        self.forward_edges: dict[PortID, set[PortID]] = {}
        self.backward_edges: dict[PortID, PortID] = {}

    # --- 単純な内部補助関数 ---
    def _get_equipment(self, port_id: PortID) -> EquipmentInstance:
        return self.equipments[self.ports[port_id].equipment_id]

    def _add_equipment(self, eq: EquipmentInstance) -> None:
        self.equipments[eq.id] = eq

    def _add_port(self, port: PortInstance) -> None:
        self.ports[port.id] = port
        if port.direction == PortDirection.OUT:
            self.forward_edges.setdefault(port.id, set())

    # --- 登録・基本操作 ---

    def add_equipment(self, eq: EquipmentDTO) -> None:
        """AudioPatchシステムに機材とポート、その内部配線を追加する。"""
        duplicates = self.ports.keys() & eq.ports.keys()
        if duplicates:
            raise DuplicateIDError(duplicates)

        self._add_equipment(eq.equipment)
        self.ports |= eq.ports
        self.forward_edges |= eq.downstream_edges
        self.backward_edges |= eq.upstream_edges

    def connect_ports(self, port_a_id: PortID, port_b_id: PortID) -> None:
        """物理的な結線（方向は自動でOUT->INに正規化）"""
        if port_a_id not in self.ports:
            raise PortNotFoundError(port_a_id, "接続元ポート")
        if port_b_id not in self.ports:
            raise PortNotFoundError(port_b_id, "接続先ポート")

        p_a = self.ports[port_a_id]
        p_b = self.ports[port_b_id]

        if p_a.direction == p_b.direction:
            raise InvalidConnectionError(port_a_id, port_b_id, p_a.direction)

        out_port = p_a if p_a.direction == PortDirection.OUT else p_b
        in_port = p_b if p_a.direction == PortDirection.OUT else p_a

        # INポートの既存接続があれば上書き（古い線を抜く）
        if in_port.id in self.backward_edges:
            old_out = self.backward_edges[in_port.id]
            if old_out in self.forward_edges:
                self.forward_edges[old_out].discard(in_port.id)

        self.forward_edges.setdefault(out_port.id, set()).add(in_port.id)
        self.backward_edges[in_port.id] = out_port.id

    def get_required_conversion(
        self, out_port_id: PortID, in_port_id: PortID
    ) -> str | None:
        """物理的な整合性（オス/メス）を判定し、必要な変換を返す"""
        if out_port_id not in self.ports:
            raise PortNotFoundError(out_port_id)
        if in_port_id not in self.ports:
            raise PortNotFoundError(in_port_id)

        out_p = self.ports[out_port_id]
        in_p = self.ports[in_port_id]

        if out_p.gender == in_p.gender:
            return "要 M-M変換" if out_p.gender == PortGender.MALE else "要 F-F変換"
        return None

    # --- グラフ探索 (Generatorで分離) ---

    def _get_next_upstream_ports(self, port_id: PortID) -> list[PortID]:
        """指定ポートの1つ上流（入力側）にあるポートID群を取得"""
        prev_id = self.backward_edges.get(port_id)
        return [prev_id] if prev_id is not None else []

    def _traverse_upstream(self, start_port_id: PortID) -> Iterator[PortID]:
        """ポートから上流へ向かってノードを巡回するジェネレータ"""
        visited = set()
        stack: list[PortID] = [start_port_id]
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            yield curr
            stack.extend(self._get_next_upstream_ports(curr))

    def _get_next_downstream_ports(self, port_id: PortID) -> list[PortID]:
        """指定ポートの1つ下流（出力側）にあるポートID群を取得"""
        return list(self.forward_edges.get(port_id, set()))

    def _traverse_downstream(self, start_port_id: PortID) -> Iterator[PortID]:
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
    # 不要な気がするので封印
    '''
    def auto_patch_mixer_from_stagebox(
        self, mixer_in_port_id: PortID, stagebox_eq_id: EquipmentID, ch_no: int
    ) -> EquipmentInstance | None:
        """マルチの番号を指定してミキサーに繋ぐ。成功した場合、上流の楽器を返す。"""
        if mixer_in_port_id not in self.ports:
            raise PortNotFoundError(mixer_in_port_id, "ミキサー入力ポート")

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
            raise PortNotFoundError(
                PortID(f"{stagebox_eq_id}_Ch{ch_no}"),
                "指定されたStageBoxの出力ポートが存在しません",
            )

        self.connect_ports(sb_out_port.id, mixer_in_port_id)

        # 上流を探索して楽器を特定する
        for port_id in self._traverse_upstream(sb_out_port.id):
            eq = self.equipments[self.ports[port_id].equipment_id]
            if eq.type in (NodeType.INSTRUMENT, NodeType.MIC):
                return eq
        return None
    '''

    def auto_patch_mixer_from_instrument(
        self, mixer_in_port_id: PortID, instrument_eq_id: EquipmentID
    ) -> PortInstance:
        """楽器を指定し、マルチを経由してミキサーに繋ぐ。成功した場合、経由したマルチのポートを返す。"""
        if mixer_in_port_id not in self.ports:
            raise PortNotFoundError(mixer_in_port_id, "ミキサー入力ポート")

        out_ports = [
            p
            for p in self.ports.values()
            if p.equipment_id == instrument_eq_id and p.direction == PortDirection.OUT
        ]
        if not out_ports:
            raise RouteNotFoundError(instrument_eq_id, "出力ポート")

        # 下流を探索してマルチのOUTを探す
        sb_out_port = None
        for port_id in self._traverse_downstream(out_ports[0].id):
            port = self.ports[port_id]
            eq = self.equipments[port.equipment_id]
            if (
                eq.type == EquipmentCategory.MULTI_BOX
                and port.direction == PortDirection.OUT
            ):
                sb_out_port = port
                break

        if not sb_out_port:
            raise RouteNotFoundError(
                instrument_eq_id, EquipmentCategory.MULTI_BOX.value
            )

        self.connect_ports(sb_out_port.id, mixer_in_port_id)
        return sb_out_port

    # =====長さ・経路取得系関数=====

    def get_upstream_port_count(self, start_port_id: PortID) -> int:
        if start_port_id not in self.ports:
            raise PortNotFoundError(start_port_id)

        visited = set()
        stack = [(start_port_id, 1)]
        max_length = 0

        while stack:
            curr_id, current_depth = stack.pop()

            if curr_id in visited:
                continue
            visited.add(curr_id)

            max_length = max(max_length, current_depth)

            upstream_ports = self._get_next_upstream_ports(curr_id)
            stack.extend([(port_id, current_depth + 1) for port_id in upstream_ports])

        return max_length

    def get_downstream_port_count(self, start_port_id: PortID) -> int:
        if start_port_id not in self.ports:
            raise PortNotFoundError(start_port_id)

        stack = [(start_port_id, 0, {start_port_id})]
        max_length = 0

        while stack:
            curr_id, current_depth, current_path = stack.pop()

            max_length = max(max_length, current_depth)

            downstream_ports = self._get_next_downstream_ports(curr_id)

            for next_port in downstream_ports:
                if next_port in current_path:
                    continue

                new_path = current_path.copy()
                new_path.add(next_port)
                stack.append((next_port, current_depth + 1, new_path))

        return max_length

    def get_upstream_ports(self, start_port_id: PortID) -> list[PortID]:
        """指定されたポート起点で、上流（入力側）へ辿れるすべてのポートIDのリストを返します。

        例: [start_port_id, upstream_1, upstream_2, ...]
        """
        if start_port_id not in self.ports:
            raise PortNotFoundError(start_port_id)
        return list(self._traverse_upstream(start_port_id))

    def get_downstream_equipment_length(self, start_port_id: PortID) -> int:
        if start_port_id not in self.ports:
            raise PortNotFoundError(start_port_id)

        stack = [(start_port_id, 1, {start_port_id})]
        max_eq_length = 0

        while stack:
            curr_port_id, current_eq_count, current_path = stack.pop()
            curr_eq_id = self.ports[curr_port_id].equipment_id

            max_eq_length = max(max_eq_length, current_eq_count)

            downstream_ports = self._get_next_downstream_ports(curr_port_id)

            for next_port_id in downstream_ports:
                if next_port_id in current_path:
                    continue

                next_eq_id = self.ports[next_port_id].equipment_id

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

    def build_chain(out_id: PortID, in_id: PortID) -> str:
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
        if not sys._get_next_upstream_ports(out_id):
            for in_id in in_ids:
                print(build_chain(out_id, in_id))
                is_empty = False

    if is_empty:
        print("結線がありません。")


def print_all_connections(sys: AudioPatchSystem):
    """【表示機能 2】全てのパッチ（結線）リストを列挙表示する"""
    print("=== 現在のパッチリスト ===")
    for out_id, in_ids in sys.forward_edges.items():
        out_p = sys.ports[out_id]
        out_eq = sys.equipments[out_p.equipment_id]

        for in_id in in_ids:
            in_p = sys.ports[in_id]
            in_eq = sys.equipments[in_p.equipment_id]
            print(
                f"OUT: {out_eq.name} ({out_p.name}) => IN: {in_eq.name} ({in_p.name})"
            )
