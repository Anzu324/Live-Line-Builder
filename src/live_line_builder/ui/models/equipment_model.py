from typing import Any

from PySide6.QtCore import QAbstractTableModel, Qt

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
)

"""
ここのモデルは機器の情報であってライブでどのように接続するかの情報でない。
どのような名前のどのような種類のどんな端子を持った機器であるかを定義するもの。
"""


# 各機材の情報を保持するモデルクラス
class EquipmentModel(QAbstractTableModel):
    def __init__(self, data: EquipmentDefinition, parent=None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        if self._data:
            return self._data.column_size()
        return 0

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            val = self._data.get_value(index.row(), index.column())
            return "" if val is None else str(val)
        return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                headers = [i.header for i in self._data.columns]
                return headers[section]
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None

    def flags(self, index):
        flags = super().flags(index)
        if (
            0 <= index.column() < len(self._data.columns)
            and self._data.columns[index.column()].editable
        ):
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            success = self._data.set_value(index.row(), index.column(), value)
            if success:
                self.dataChanged.emit(index, index)
                return True
            return False
        return False

    def get_product_at(self, row: int) -> dict[str, Any] | None:
        """指定した行のデータ（辞書）をそのまま返すヘルパーメソッド"""
        if 0 <= row < len(self._data):
            return self._data.get_row(row).model_dump()
        return None


# 各機材の各コネクタの情報を保持するモデルクラス
class EquipmentPortModel(QAbstractTableModel):
    def __init__(self, data: EquipmentPortDefinition, parent=None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        if self._data:
            return self._data.count_column()
        return 0

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            val = self._data.get_value(index.row(), index.column())
            return "" if val is None else str(val)
        return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                headers = [i.header for i in self._data.columns]
                return headers[section]
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None

    def flags(self, index):
        flags = super().flags(index)
        if (
            0 <= index.column() < len(self._data.columns)
            and self._data.columns[index.column()].editable
        ):
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            success = self._data.set_value(index.row(), index.column(), value)
            if success:
                self.dataChanged.emit(index, index)
                return True
            return False
        return False
