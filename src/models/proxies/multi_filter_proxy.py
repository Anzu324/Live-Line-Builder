from PySide6.QtCore import QSortFilterProxyModel, Qt


# プロキシモデルのクラス
# プロキシモデルとは、元のモデルのデータを加工して表示するためのモデルです。
class MultiFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_column = 0  # 対象の列
        self._search_value = ""  # 検索したい値
        self._hidden_columns = set()  # 非表示にしたい列番号（インデックス）
        self._hidden_columns.add(2)  # 例: 列2を非表示にする場合は、ここで追加する
        self._hidden_columns.add(3)  # 例: 列3を非表示にする場合は、ここで追加する

    def set_filter_condition(self, column: int, value: str):
        """検索対象の列と値をセットするメソッド"""
        self._target_column = column
        self._search_value = value
        self.invalidateFilter()  # フィルターを再計算させる

    def filterAcceptsRow(self, source_row, source_parent):
        """1行ごとに表示するかどうか（True/False）を判定するQtの内部関数"""
        # 検索値が空なら全行表示する
        if not self._search_value:
            return True

        # 元Modelから「指定した行・列」のセル位置を取得
        source_model = self.sourceModel()
        index = source_model.index(source_row, self._target_column, source_parent)

        # セルの値（文字列）を取得
        cell_value = str(source_model.data(index, Qt.ItemDataRole.DisplayRole))

        # ★ 完全一致チェック（一致していれば True を返して表示）
        return cell_value == self._search_value

    def filterAcceptsColumn(self, source_column, source_parent):
        """★ Qtの内部関数: 1列ごとに表示するかどうか（True/False）を判定"""
        # 非表示リストに入っている列なら False (除外) を返す
        return source_column not in self._hidden_columns
