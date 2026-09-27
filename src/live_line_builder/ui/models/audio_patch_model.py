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
        self._data = data  # 2次元リストなどのデータを保持
        self._base_point_equipment_id: EquipmentID | None = (
            None if base_point_id is None else EquipmentID(base_point_id)
        )  # 基点となる機材のID
        self._stream = stream  # 入力または出力ストリームを指定
        self.filtered_dict: list[PortInstance] = (
            []
            if base_point_id == None
            else pre_set_filterd_dict(self._data, EquipmentID(base_point_id))
        )  # フィルターされたリストを生成。

    # 必須: 行数を返す
    def rowCount(self, parent=None):
        if self._base_point_equipment_id is None:
            return 0
        return len(self.filtered_dict)

    # 必須: 列数を返す
    def columnCount(self, parent=None):
        if self._data is None:
            return 0
        target_ports = [
            i.id
            for i in self._data.ports.values()
            if i.equipment_id == self._base_point_equipment_id
        ]
        max_length = 0
        for i in target_ports:
            stream_length = self._data.get_upstream_port_count(i)
            max_length = max(max_length, stream_length)
        return max_length * 3

    # 必須: データを返す
    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        filtered_dict = self.filtered_dict
        if not index.isValid():
            return None
        # DisplayRoleは「画面に文字として表示するためのデータ」を要求された時
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return filtered_dict[index.row()].equipment_id
            if index.column() == 1:
                return filtered_dict[index.row()].name
            return "1"  # str(self._data[index.row(), index.column()])
        return

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

        self.filtered_dictを設定する。これはCountやdataを呼ばれる。
        """
        filtered_start_dict: list[PortInstance] = [
            v
            for v in self._data.ports.values()
            if v.equipment_id == self._base_point_equipment_id
        ]

        self.filtered_dict = [
            v
            for v in self._data.ports.values()
            if v.equipment_id == self._base_point_equipment_id
        ]


# __init__内でset_filterd_dicが呼べないので同等機能の関数。
def pre_set_filterd_dict(
    data, base_point_equipment_id: EquipmentID
) -> list[PortInstance]:
    """フィルタリングされた情報を更新して属性に保持"""
    return [v for v in data.ports.values() if v.equipment_id == base_point_equipment_id]
