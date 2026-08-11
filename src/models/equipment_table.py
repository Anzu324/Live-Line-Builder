from PySide6.QtCore import QAbstractTableModel, Qt


# 各機材の情報を保持するモデルクラス
class EquipmentModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
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
            return str(self._data[index.row()][index.column()])
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
    def get_product_at(self, row: int) -> list[str] | None:
        """指定した行のデータ（辞書）をそのまま返すヘルパーメソッド"""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None


# 各機材の各コネクタの情報を保持するモデルクラス
class EquipmentConnectorModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
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
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # 列のヘッダー
                headers = ["EQUIPMENT", "NAME", "CONNECTOR TYPE", "IN/OUT"]
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
