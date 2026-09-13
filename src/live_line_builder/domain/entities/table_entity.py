from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal, TypeIs

# 📌 型エイリアスの定義
type RawValue = int | str | bool
# AllowedType は「型オブジェクトそのもの（intクラス, strクラス, boolクラス）」を表す
type AllowedType = type[int | str | bool]
type AllowedTypeName = Literal["int", "str", "bool"]

STR_TO_TYPE: dict[str, AllowedType] = {"int": int, "str": str, "bool": bool}


# 📌 1. 型チェッカーに「RawValue型であること」を完全に理解させるための関数を追加
def is_raw_value(val: Any) -> TypeIs[RawValue]:
    """val が RawValue (int | str | bool) のいずれかであるかを判定する型ガード"""
    return isinstance(val, (int, str, bool))


@dataclass
class Column:
    key: str  # 内部での識別子（例: "hp"）
    header: str  # UIに表示するヘッダー名（例: "体力"）
    data_type: AllowedType  # 型（例: int, str）
    default: Any = None  # 初期値
    editable: bool = True  # UIで編集可能か


class TableEntity:
    """columns: テーブル型のエンティティの列を指定。__init__無くとも簡易的に切り替えできる。"""

    columns: ClassVar[list[Column]] = []

    def __init__(self, rows: list[dict[str, RawValue]] | None = None):
        # 中身は [{"id": "p01", "name": "頭部", "hp": 100}, ...] のような辞書リスト
        self.rows: list[dict[str, RawValue]] = rows or []

    def count_column(self) -> int:
        return len(self.columns)

    def get_value(self, row_idx: int, col_idx: int) -> RawValue | None:
        col_key = self.columns[col_idx].key
        result = self.rows[row_idx].get(col_key, self.columns[col_idx].default)

        # ⭕ 作成した型ガード関数を使用
        if is_raw_value(result):
            return result
        return None

    def set_value(self, row_idx: int, col_idx: int, value: RawValue) -> bool:
        col = self.columns[col_idx]
        try:
            # ⭕ col.data_type(value) の動的型変換
            typed_value = col.data_type(value)
            # typed_value が RawValue の型を満たしていることを保証
            if isinstance(typed_value, RawValue.__value__):
                self.rows[row_idx][col.key] = typed_value
                return True
            return False
        except ValueError, TypeError:  # ⭕ 構文エラーを修正 (タプル化)
            return False

    def __getitem__(self, item: tuple[int, int | str]) -> RawValue | None:
        """entity[行, 列(インデックスまたはキー)] によるアクセスを提供"""
        if isinstance(item, tuple) and len(item) == 2:
            row_idx, col = item
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col
            return self.rows[row_idx].get(col_key)
        return None

    def get_item(self, row: int, column: str) -> RawValue | None:
        return self.__getitem__((row, column))

    def get_row(self, item: int) -> dict[str, RawValue]:
        return self.rows[item]

    def __setitem__(
        self, key: tuple[int, int | str] | int, value: RawValue | dict[str, RawValue]
    ) -> None:
        """entity[行, 列] = 値、または entity[行] = 辞書 の両方に対応"""
        if isinstance(key, tuple) and len(key) == 2:
            row_idx, col = key
            if isinstance(col, int):
                col_key = self.columns[col].key
            else:
                col_key = col

            # ⭕ 作成した型ガード関数を使用
            # これにより、型チェッカーはこの if 文の中で value を「100% RawValue 型」と認識します
            if is_raw_value(value):
                self.rows[row_idx][col_key] = value

        elif isinstance(key, int):
            # ⭕ 行丸ごとの置換（value が辞書である必要がある）
            if isinstance(value, dict):
                self.rows[key] = value

    def set_row(self, row: int, value: dict[str, RawValue]) -> None:
        if row < 0 or row >= len(self.rows):
            return
        self.rows[row] = value

    def append_row(self, value: dict[str, RawValue]) -> None:
        self.rows.append(value)

    def insert(self, index: int, object: dict[str, RawValue]) -> None:
        self.rows.insert(index, object)

    def __delitem__(self, key: int) -> None:
        if key < 0 or key >= len(self.rows):
            return
        self.rows.__delitem__(key)

    def __len__(self) -> int:
        return len(self.rows)

    def column_size(self) -> int:
        return len(self.columns)


def zip_column_key_and_table(
    keys: list[str],
    values: Sequence[Sequence[RawValue]],  # ⭕ list から Sequence に変更（共変にする）
) -> list[dict[str, RawValue]]:
    """外部データを TableEntity 用の辞書リストに変換するヘルパー関数"""
    dic: list[dict[str, RawValue]] = []
    for i in values:
        dic.append(dict(zip(keys, i)))
    return dic
