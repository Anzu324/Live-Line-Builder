from enum import Enum

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
)

from live_line_builder.domain.line_graph.audio_patch import (
    AudioPatchSystem,
    EquipmentCategory,
    EquipmentID,
    EquipmentInstance,
    PortInstance,
)

"""
ここのモデルは機器の情報であってライブでどのように接続するかの情報でない。
どのような名前のどのような種類のどんな端子を持った機器であるかを定義するもの。
"""


class AudioPatchSystemAttributesModel(QObject):
    """AudioPatchSystemの属性へのアクセスを提供する。

    例:機材数やポート数など統計的な情報。
    個別の部分への直接のアクセスは提供しない。
    """

    def __init__(self, entity: AudioPatchSystem):
        super().__init__()
        self._entity = entity

    @property
    def gateway_equipments_name(self) -> list[str]:
        """ミキサーやマルチなど表示起点になれる機材だけをリストアップして名前を返す"""
        # TODO:フィルタリング機能は未実装。
        if self._entity is None:
            return []
        return [
            eq.name
            for eq in self._entity.equipments.values()
            if eq.type in [EquipmentCategory.MIXER, EquipmentCategory.MULTI_BOX]
        ]

    @property
    def gateway_equipments(self) -> list[EquipmentInstance]:
        """ミキサーやマルチなど表示起点になれる機材だけをリストアップして名前を返す"""
        # TODO:フィルタリング機能は未実装。
        if self._entity is None:
            return []
        return [
            eq
            for eq in self._entity.equipments.values()
            if eq.type in [EquipmentCategory.MIXER, EquipmentCategory.MULTI_BOX]
        ]

    @property
    def get_raw_entity(self) -> AudioPatchSystem:
        return self._entity


class Stream(Enum):
    INPUT = "Input"
    OUTPUT = "Output"


# パッチ情報を表にまとめて表示するためのモデル。未完。
class PatchTableModel(QAbstractTableModel):
    def __init__(
        self,
        data: AudioPatchSystem,
        base_point_id: str | None = None,
        stream: Stream = Stream.INPUT,
        parent=None,
    ):
        super().__init__(parent)
        self._data = data
        self._base_point_equipment_id: EquipmentID | None = (
            None if base_point_id is None else EquipmentID(base_point_id)
        )
        self._stream = stream
        self.filtered_dict: list[list[PortInstance]] = (
            [] if base_point_id is None else self._build_filtered_ports()
        )

    def _build_filtered_ports(self) -> list[list[PortInstance]]:
        if self._base_point_equipment_id is None:
            return []

        start_ports = [
            port
            for port in self._data.ports.values()
            if port.equipment_id == self._base_point_equipment_id
        ]

        return [
            [
                self._data.ports[port_id]
                for port_id in self._data.get_upstream_ports(port.id)
            ]
            for port in start_ports
        ]

    # 必須: 行数を返す
    def rowCount(self, parent=None):
        if self._base_point_equipment_id is None:
            return 0
        return len(self.filtered_dict)

    # 必須: 列数を返す
    def columnCount(self, parent=None):
        if self._data is None or self._base_point_equipment_id is None:
            return 0
        if not self.filtered_dict:
            return 0

        max_row_length = max(len(row) for row in self.filtered_dict)
        return max_row_length * 3

    def _cell_value_for_index(self, row_index: int, column_index: int) -> str | None:
        if not 0 <= row_index < len(self.filtered_dict):
            return None

        row = self.filtered_dict[row_index]
        if not row:
            return None

        # 既存のテーブル設計では列幅を 3 で見ていたため、実際の行長より広く確保している。
        # そのため、表示上の列インデックスが行の長さを超えても、実データ側は先頭要素を返す。
        if column_index < 0:
            return None

        port_index = min(column_index, len(row) - 1)
        port = row[port_index]
        return port.name if isinstance(port, PortInstance) else str(port)

    # 必須: データを返す
    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        return self._cell_value_for_index(index.row(), index.column())

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列のヘッダー
                headers = range(self.columnCount())
                return str(headers[section])
            if orientation == Qt.Orientation.Vertical:
                # 行のヘッダー（1, 2, 3...と表示する場合）
                return str(section + 1)
        return None

    def flags(self, index):
        # 基本的な選択・有効状態に加えて、編集可能フラグを足す
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def change_base_point(self, point: str, stream: Stream):
        self.beginResetModel()  # リセット開始を通知
        self._base_point_equipment_id = EquipmentID(point)
        self._stream = stream
        self.set_filterd_dict()
        self.endResetModel()  # リセット完了を通知（Viewが全再描画される）

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            # 入力されたvalueをデータに反映
            # self._data[index.row()][index.column()] = value
            # データが変更されたことをViewに通知（これがないと画面が更新されない）
            self.dataChanged.emit(index, index)
            return True
        return False

    def set_filterd_dict(self):
        """フィルタリングされた情報を更新して属性に保持

        self.filtered_dictは各行が上流へ辿った `PortInstance` の列を持つ。
        """
        self.filtered_dict = self._build_filtered_ports()


# __init__内でset_filterd_dicが呼べないので同等機能の関数。
def pre_set_filterd_dict(
    data: AudioPatchSystem, base_point_equipment_id: EquipmentID
) -> list[list[PortInstance]]:
    """指定機材から上流へ辿れるポート情報の2次元リストを返す。"""
    start_ports = [
        port
        for port in data.ports.values()
        if port.equipment_id == base_point_equipment_id
    ]
    return [
        [data.ports[port_id] for port_id in data.get_upstream_ports(port.id)]
        for port in start_ports
    ]
