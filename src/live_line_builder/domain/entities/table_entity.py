from dataclasses import dataclass
from typing import Any, ClassVar, Literal

type AllowedType = type[int | str]
# 📌 文字列から本物の「型クラス」を呼び出すためのマッピングを用意
type RawValue = int | str | bool
# JSON保存用の文字列リテラル型
type AllowedTypeName = Literal["int", "str"]

STR_TO_TYPE: dict[str, AllowedType] = {
    "int": int,
    "str": str,
}


@dataclass
class Column:
    key: str  # 内部での識別子（例: "hp"）
    header: str  # UIに表示するヘッダー名（例: "体力"）
    data_type: AllowedType  # 型（例: int, str）
    default: Any = None  # 初期値
    editable: bool = True  # UIで編集可能か


class TableEntity:
    """
    columns: テーブル型のエンティティの列を指定。__init__無くとも簡易的に切り替えできる。
    """

    columns: ClassVar[list[Column]] = []

    def __init__(self, rows: list[dict[str, RawValue]] | None = None):
        # 中身は [{"id": "p01", "name": "頭部", "hp": 100}, ...] のような辞書リスト
        self.rows: list[dict[str, RawValue]] = rows or []

    def count_column(self) -> int:
        return len(self.columns)

    def get_value(self, row_idx: int, col_idx: int) -> RawValue | None:
        col_key = self.columns[col_idx].key
        return self.rows[row_idx].get(col_key, self.columns[col_idx].default)

    # 修正後のメソッド
    def set_value(self, row_idx: int, col_idx: int, value: RawValue) -> bool:
        col = self.columns[col_idx]
        try:
            # Pylanceもmypyも「Call可能」だと納得します
            typed_value = col.data_type(value)
            self.rows[row_idx][col.key] = typed_value
            return True
        except ValueError, TypeError:
            return False

    # []によるアクセスを提供
    def __getitem__(self, item: tuple[int, str]) -> RawValue | None:
        # タプル指定の場合: entity[行, 列]
        if isinstance(item, tuple):
            row_idx, col = item
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col
            return self.rows[row_idx].get(col_key)

    def get_item(self, row: int, column: str) -> RawValue | None:
        return self.__getitem__((row, column))

    def get_row(self, item: int) -> dict[str, RawValue] | None:
        if item < 0 or item >= len(self.rows):
            return None
        return self.rows[item]

    def __setitem__(self, key: tuple[int, str], value: RawValue):
        if isinstance(key, tuple):
            row_idx, col = key
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col
            self.rows[row_idx][col_key] = value
        else:
            self.rows[key] = value

    def set_row(self, row: int, value: dict[str, RawValue]) -> None:
        if row < 0 or row >= len(self.rows):
            return
        self.rows[row] = value

    def append_row(self, value: dict[str, RawValue]) -> None:
        self.rows.append(value)

    def insert(self, index: int, object: dict[str, RawValue]) -> None:
        self.rows.insert(index, object)

    def __delitem__(self, key):
        if key < 0 or key >= len(self.rows):
            return
        self.rows.__delitem__(key)

    # リスト代わりの機能を提供
    # 長さを返す
    def __len__(self) -> int:
        return len(self.rows)

    def column_size(self) -> int:
        return len(self.columns)


def zip_column_key_and_table(
    keys: list[str], values: list[list[str]]
) -> list[dict[str, Any]]:
    dic = []
    for i in values:
        dic.append(dict(zip(keys, i)))
    return dic
