from PySide6.QtCore import QAbstractTableModel, Qt

from live_line_builder.domain.entities import EquipmentEntity, EquipmentPortEntity

"""
ここのモデルは機器の情報であってライブでどのように接続するかの情報でない。
どのような名前のどのような種類のどんな端子を持った機器であるかを定義するもの。
"""


# 各機材の情報を保持するモデルクラス
class EquipmentModel(QAbstractTableModel):
    def __init__(self, data: EquipmentEntity, parent=None):
        super().__init__(parent)
        self._data = data  # 2次元リストなどのデータを保持

    # 必須: 行数を返す
    def rowCount(self, parent=None):
        return len(self._data)

    # 必須: 列数を返す
    def columnCount(self, parent=None):
        if self._data:
            return self._data.column_size()
        return 0

    # 必須: データを返す
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        # DisplayRoleは「画面に文字として表示するためのデータ」を要求された時
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列のヘッダー
                headers = ["ID", "NAME", "TYPE"]
                return headers[section]
            if orientation == Qt.Orientation.Vertical:
                # 行のヘッダー（1, 2, 3...と表示する場合）
                return str(section + 1)
        return None

    def flags(self, index):
        # 基本的な選択・有効状態に加えて、編集可能フラグを足す
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            # 入力されたvalueをデータに反映
            self._data[index.row()][index.column()] = value
            # データが変更されたことをViewに通知（これがないと画面が更新されない）
            self.dataChanged.emit(index, index)
            return True
        return False

    # 独自メソッド
    def get_product_at(self, row: int) -> dict[str, str] | None:
        """指定した行のデータ（辞書）をそのまま返すヘルパーメソッド"""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None


# 各機材の各コネクタの情報を保持するモデルクラス
class EquipmentPortModel(QAbstractTableModel):
    def __init__(self, data: EquipmentPortEntity, parent=None):
        super().__init__(parent)
        self._data = data  # 2次元リストなどのデータを保持

    # 必須: 行数を返す
    def rowCount(self, parent=None):
        return len(self._data)

    # 必須: 列数を返す
    def columnCount(self, parent=None):
        if self._data:
            return len(self._data[0])
        return 0

    # 必須: データを返す
    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        # DisplayRoleは「画面に文字として表示するためのデータ」を要求された時
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列のヘッダー
                headers = ["EQUIPMENT", "NAME", "CONNECTOR", "IN/OUT"]
                return headers[section]
            if orientation == Qt.Orientation.Vertical:
                # 行のヘッダー（1, 2, 3...と表示する場合）
                return str(section + 1)
        return None

    def flags(self, index):
        # 基本的な選択・有効状態に加えて、編集可能フラグを足す
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            # 入力されたvalueをデータに反映
            self._data[index.row(), index.column()] = value
            # データが変更されたことをViewに通知（これがないと画面が更新されない）
            self.dataChanged.emit(index, index)
            return True
        return False
