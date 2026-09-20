from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, TypeVar, cast

from pydantic import BaseModel, ConfigDict, ValidationError


class TableRowModel(BaseModel):
    """テーブルの1行を表すPydanticベースのモデル基底クラス"""

    model_config = ConfigDict(validate_assignment=True)

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise KeyError(key)
        setattr(self, key, value)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in type(self).model_fields

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> dict[str, Any]:
        """行データを辞書として取得"""
        return self.model_dump()


@dataclass
class Column:
    key: str  # モデルの属性名（例: "quantity"）
    header: str  # UIに表示するヘッダー名（例: "数量"）
    editable: bool = True  # UIで編集可能か
    default: Any = None  # 初期値


RowT = TypeVar("RowT", bound=TableRowModel)


class TableEntity[RowT: TableRowModel]:
    """columns: テーブル型のエンティティの列を指定。__init__無くとも簡易的に切り替えできる。"""

    row_type: ClassVar[type[TableRowModel]] = TableRowModel
    columns: ClassVar[list[Column]] = []

    def _coerce_row(self, value: RowT | dict[str, Any]) -> RowT:
        if isinstance(value, self.row_type):
            return cast(RowT, value)
        if isinstance(value, dict):
            return cast(RowT, self.row_type.model_validate(value))
        raise TypeError(f"Unsupported row value: {type(value)!r}")

    def __init__(self, rows: Sequence[RowT | dict[str, Any]] | None = None):
        self.rows: list[RowT] = []
        if rows:
            for raw_row in rows:
                self.rows.append(self._coerce_row(raw_row))

    def count_column(self) -> int:
        return len(self.columns)

    def column_size(self) -> int:
        return len(self.columns)

    def _key_to_col_idx(self, key: str) -> int | None:
        for idx, col in enumerate(self.columns):
            if col.key == key:
                return idx
        return None

    def get_value(self, row_idx: int, col_idx: int) -> Any:
        if 0 <= row_idx < len(self.rows) and 0 <= col_idx < len(self.columns):
            col_key = self.columns[col_idx].key
            return getattr(self.rows[row_idx], col_key, self.columns[col_idx].default)
        return None

    def set_value(self, row_idx: int, col_idx: int, value: Any) -> bool:
        """指定位置のセルに値をセットする。Pydanticによる自動型変換とバリデーションが働く。"""
        if not (0 <= row_idx < len(self.rows) and 0 <= col_idx < len(self.columns)):
            return False
        col = self.columns[col_idx]
        if not col.editable:
            return False
        row = self.rows[row_idx]
        try:
            setattr(row, col.key, value)
            return True
        except ValueError, TypeError, ValidationError:
            return False

    def __getitem__(self, item: tuple[int, int | str] | int) -> Any:
        """entity[行, 列(インデックスまたはキー)] によるアクセスを提供"""
        if isinstance(item, tuple) and len(item) == 2:
            row_idx, col = item
            if not (0 <= row_idx < len(self.rows)):
                return None
            if isinstance(col, int):
                if 0 <= col < len(self.columns):
                    col_key = self.columns[col].key
                    return getattr(self.rows[row_idx], col_key, None)
                return None
            else:
                return getattr(self.rows[row_idx], col, None)
        elif isinstance(item, int):
            return self.rows[item]
        return None

    def get_item(self, row: int, column: str) -> Any:
        return self.__getitem__((row, column))

    def get_row(self, item: int) -> RowT:
        return self.rows[item]

    def __setitem__(self, key: tuple[int, int | str] | int, value: Any) -> None:
        """entity[行, 列] = 値、または entity[行] = 行モデル/辞書 の両方に対応"""
        if isinstance(key, tuple) and len(key) == 2:
            row_idx, col = key
            if isinstance(col, int):
                self.set_value(row_idx, col, value)
            else:
                col_idx = self._key_to_col_idx(col)
                if col_idx is not None:
                    self.set_value(row_idx, col_idx, value)
                elif 0 <= row_idx < len(self.rows):
                    try:
                        setattr(self.rows[row_idx], col, value)
                    except ValueError, TypeError, ValidationError:
                        pass
        elif isinstance(key, int):
            if 0 <= key < len(self.rows):
                self.rows[key] = self._coerce_row(value)

    def set_row(self, row: int, value: RowT | dict[str, Any]) -> None:
        if 0 <= row < len(self.rows):
            self.rows[row] = self._coerce_row(value)

    def append_row(self, value: RowT | dict[str, Any]) -> None:
        self.rows.append(self._coerce_row(value))

    def insert(self, index: int, object: RowT | dict[str, Any]) -> None:
        self.rows.insert(index, self._coerce_row(object))

    def __delitem__(self, key: int) -> None:
        if 0 <= key < len(self.rows):
            del self.rows[key]

    def __len__(self) -> int:
        return len(self.rows)


def zip_column_key_and_table(
    keys: list[str],
    values: Sequence[Sequence[Any]],
) -> list[dict[str, Any]]:
    """外部データを TableEntity 用の辞書リストに変換するヘルパー関数"""
    dic: list[dict[str, Any]] = []
    for i in values:
        dic.append(dict(zip(keys, i)))
    return dic
