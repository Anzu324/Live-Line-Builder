from PySide6.QtCore import QAbstractTableModel, QObject, Qt

from live_line_builder.domain.line_graph import AudioPatchSystem, NodeType

"""
ここのモデルは機器の情報であってライブでどのように接続するかの情報でない。
どのような名前のどのような種類のどんな端子を持った機器であるかを定義するもの。
"""


class AudioPatchSystemAttributesModel(QObject):
    """AudioPatchSystemの属性へのアクセスを提供する。

    例:機材数やポート数など統計的な情報。
    個別の部分への直接のアクセスは提供しない。
    """

    def __init__(self, entity: AudioPatchSystem | None = None):
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
            if eq.type in [NodeType.MIXER, NodeType.MULTI_BOX]
        ]


# パッチ情報を表にまとめて表示するためのモデル。未完。
class PatchTableModel(QAbstractTableModel):
    def __init__(self, data: AudioPatchSystem, base_point_id: str, parent=None):
        super().__init__(parent)
        self._data = data  # 2次元リストなどのデータを保持
        self._base_point_equipment_id = base_point_id  # 基点となる機材のID

    # 必須: 行数を返す
    def rowCount(self, parent=None):
        filtered_dict = {
            k: v
            for k, v in self._data.ports.items()
            if v.equipment_id == self._base_point_equipment_id
        }
        return len(filtered_dict)

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
            stream_length = self._data.get_upstream_length(i)
            max_length = max(max_length, stream_length)
        return max_length * 3

    # 必須: データを返す
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        # DisplayRoleは「画面に文字として表示するためのデータ」を要求された時
        if role == Qt.ItemDataRole.DisplayRole:
            return 1  # str(self._data[index.row(), index.column()])
        return

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列のヘッダー
                headers = range(self.columnCount())
                return headers[section]
            if orientation == Qt.Orientation.Vertical:
                # 行のヘッダー（1, 2, 3...と表示する場合）
                return str(section + 1)
        return None

    def flags(self, index):
        # 基本的な選択・有効状態に加えて、編集可能フラグを足す
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    # def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
    #     if role == Qt.ItemDataRole.EditRole:
    #         # 入力されたvalueをデータに反映
    #         self._data[index.row()][index.column()] = value
    #         # データが変更されたことをViewに通知（これがないと画面が更新されない）
    #         self.dataChanged.emit(index, index)
    #         return True
    #     return False
