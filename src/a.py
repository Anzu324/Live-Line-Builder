"""
AIが参考までに作ったやつなのできにせんといて。
"""

import sys

from PySide6.QtCore import QModelIndex, QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QStyledItemDelegate,
    QTableView,
)


# --------------------------------------------------
# 1. 画像とテキストを綺麗に描くカスタムデリゲート
# --------------------------------------------------
class WiringTableDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index: QModelIndex):
        painter.save()
        rect = option.rect

        # 枠線を描画
        painter.setPen(QColor(200, 200, 200))
        painter.drawRect(rect)

        # セルのデータを取得
        data = index.data(Qt.UserRole)

        # データがただの文字列（破線 "-----" など）の場合
        if isinstance(data, str):
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(rect, Qt.AlignCenter, data)

        # データが辞書（画像やテキストの情報を持つリッチデータ）の場合
        elif isinstance(data, dict):
            cell_type = data.get("type")

            # --- A. 機材セル (名前 + 種別 + 写真) ---
            if cell_type == "equipment":
                name = data.get("name", "")
                category = data.get("category", "")

                # テキスト描画 (上部)
                font_bold = QFont()
                font_bold.setBold(True)
                painter.setFont(font_bold)
                painter.setPen(QColor(30, 30, 30))
                painter.drawText(
                    QRect(rect.left() + 5, rect.top() + 5, rect.width() - 10, 20),
                    Qt.AlignLeft,
                    name,
                )

                painter.setFont(QFont("", 9))
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(
                    QRect(rect.left() + 5, rect.top() + 22, rect.width() - 10, 18),
                    Qt.AlignLeft,
                    category,
                )

                # 画像描画 (下部)
                img_rect = QRect(
                    rect.left() + 10,
                    rect.top() + 42,
                    rect.width() - 20,
                    rect.height() - 48,
                )
                self._draw_dummy_image(painter, img_rect, name, QColor(60, 60, 80))

            # --- B. ケーブル・マイク端子セル (ななめ配置/アイコン + 端子名) ---
            elif cell_type == "connector":
                label = data.get("label", "")

                # 画像 (上部)
                img_rect = QRect(
                    rect.left() + (rect.width() - 50) // 2, rect.top() + 10, 50, 40
                )
                self._draw_dummy_image(
                    painter, img_rect, "プラグ", QColor(100, 140, 120)
                )

                # テキスト (下部)
                font = QFont()
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(QColor(30, 30, 30))
                painter.drawText(
                    QRect(rect.left(), rect.top() + 52, rect.width(), 20),
                    Qt.AlignCenter,
                    label,
                )

            # --- C. マルチボックスセル (番号 + 機器名 + マルチ画像) ---
            elif cell_type == "multi":
                ch_num = data.get("ch", "")
                target = data.get("target", "")

                # 左側：チャンネル番号と対象名
                font_num = QFont()
                font_num.setBold(True)
                font_num.setPointSize(11)
                painter.setFont(font_num)
                painter.drawText(
                    QRect(rect.left() + 10, rect.top() + 15, 60, 20),
                    Qt.AlignCenter,
                    f"{ch_num}",
                )

                painter.setFont(QFont("", 9))
                painter.drawText(
                    QRect(rect.left() + 5, rect.top() + 38, 70, 20),
                    Qt.AlignCenter,
                    target,
                )

                # 右側：マルチボックス画像
                img_rect = QRect(rect.right() - 55, rect.top() + 10, 48, 48)
                self._draw_dummy_image(painter, img_rect, "BOX", QColor(140, 80, 80))

        painter.restore()

    def _draw_dummy_image(
        self, painter: QPainter, rect: QRect, label: str, color: QColor
    ):
        """画像ファイルの代わりにテスト用の四角と文字を描くヘルパー関数"""
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 4, 4)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("", 8))
        painter.drawText(rect, Qt.AlignCenter, label)

    def sizeHint(self, option, index) -> QSize:
        return QSize(120, 85)  # 行の高さを85pxに設定


# --------------------------------------------------
# 2. メイン画面の構築
# --------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配線接続一覧表 (舞台側) デモ")
        self.resize(800, 400)

        self.table_view = QTableView(self)
        self.model = QStandardItemModel(3, 5, self)

        # ヘッダー設定
        self.model.setHorizontalHeaderLabels(
            [
                "楽器 / 機材",
                "出力端子",
                "マイク等 / 入力",
                "出力端子",
                "マルチ / 入力端子",
            ]
        )
        self.table_view.setModel(self.model)

        # データをセット（画像内の表を再現）
        self._setup_sample_data()

        # デリゲートの適用
        self.delegate = WiringTableDelegate()
        self.table_view.setItemDelegate(self.delegate)

        # テーブルの見た目調整
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setDefaultSectionSize(85)  # 行高さを固定
        self.setCentralWidget(self.table_view)

    def _setup_sample_data(self):
        # 1行目: DSL100H + SM57 + CANARE 12ch
        self._set_cell(
            0, 0, {"type": "equipment", "name": "DSL100H", "category": "ギターアンプ"}
        )
        self._set_cell(0, 1, "")
        self._set_cell(0, 2, {"type": "connector", "label": "SM57"})
        self._set_cell(0, 3, {"type": "connector", "label": "XLR-F"})
        self._set_cell(0, 4, {"type": "multi", "ch": "1", "target": "Marshall"})

        # 2行目: Fa-07 + TRS + 破線 + Fantom
        self._set_cell(
            1, 0, {"type": "equipment", "name": "Fa-07", "category": "シンセサイザー"}
        )
        self._set_cell(1, 1, {"type": "connector", "label": "TRS"})
        self._set_cell(1, 2, "----")  # 破線表示
        self._set_cell(1, 3, "")
        self._set_cell(1, 4, {"type": "multi", "ch": "2", "target": "Fantom"})

        # 3行目: JC-120 + TS + 破線 + CPマルチ
        self._set_cell(
            2, 0, {"type": "equipment", "name": "JC-120", "category": "ギターアンプ"}
        )
        self._set_cell(2, 1, {"type": "connector", "label": "TS"})
        self._set_cell(2, 2, "----")
        self._set_cell(2, 3, "")
        self._set_cell(2, 4, {"type": "multi", "ch": "1", "target": "Fantom"})

    def _set_cell(self, row, col, data):
        item = QStandardItem()
        item.setData(data, Qt.UserRole)
        self.model.setItem(row, col, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
