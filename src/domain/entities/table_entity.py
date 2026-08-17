from dataclasses import dataclass
from typing import Any


@dataclass
class Column:
    key: str  # 内部での識別子（例: "hp"）
    header: str  # UIに表示するヘッダー名（例: "体力"）
    data_type: type  # 型（例: int, str）
    default: Any = None  # 初期値
    editable: bool = True  # UIで編集可能か


class TableEntity:
    """
    columns: テーブル型のエンティティの列を指定。__init__無くとも簡易的に切り替えできる。
    """

    columns: list[Column] = []

    def __init__(self, rows: list[dict] | None = None):
        # 中身は [{"id": "p01", "name": "頭部", "hp": 100}, ...] のような辞書リスト
        self.rows = rows or []

    def get_value(self, row_idx: int, col_idx: int) -> Any:
        col_key = self.columns[col_idx].key
        return self.rows[row_idx].get(col_key, self.columns[col_idx].default)

    def set_value(self, row_idx: int, col_idx: int, value: Any) -> bool:
        col = self.columns[col_idx]
        # 型チェック・変換をここで行う
        try:
            typed_value = col.data_type(value)
            self.rows[row_idx][col.key] = typed_value
            return True
        except ValueError, TypeError:
            return False

    # []によるアクセスを提供
    def __getitem__(self, item):
        # タプル指定の場合: entity[行, 列]
        if isinstance(item, tuple):
            row_idx, col = item
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col
            return self.rows[row_idx].get(col_key)

        # 単一指定の場合: entity[行] (辞書またはスライスが返る)
        return self.rows[item]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            row_idx, col = key
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col
            self.rows[row_idx][col_key] = value
        else:
            self.rows[key] = value

    # リスト代わりの機能を提供
    # 長さを返す
    def __len__(self):
        return len(self.rows)

    def column_size(self):
        return len(self.columns)


def zip_column_key_and_table(
    keys: list[str], values: list[list[str]]
) -> list[dict[str, Any]]:
    dic = []
    for i in values:
        dic.append(dict(zip(keys, i)))
    return dic
