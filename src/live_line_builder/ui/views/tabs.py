from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class WorkSheetTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 1. ブラウザ風タブの基本設定
        # self.setTabsClosable(True)  # タブに「×（閉じる）」ボタンを表示
        self.setMovable(True)  # タブをドラッグして並び替え可能にする

        # 2. タブの「閉じる」ボタンが押された時のシグナル接続
        # self.tabCloseRequested.connect(self.close_tab)

        # 3. 右上に「+（新規タブ）」ボタンを配置
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedWidth(25)
        self.new_tab_btn.clicked.connect(lambda: self._add_new_tab("新しいタブ"))
        self.setCornerWidget(self.new_tab_btn)

        # 初期タブを作成
        self._add_new_tab("ホーム")

    def _add_new_tab(self, title="新しいタブ"):
        # タブの中身となるページウィジェットを作成
        page = QWidget()
        layout = QVBoxLayout(page)

        # 簡易的なURLバーとコンテンツエリア
        url_layout = QHBoxLayout()
        url_input = QLineEdit()
        url_input.setPlaceholderText("URLまたは検索ワードを入力...")
        url_layout.addWidget(url_input)

        layout.addLayout(url_layout)
        layout.addWidget(QLabel(f"「{title}」のコンテンツ領域", self))

        # タブを追加し、追加したタブを選択状態にする
        index = self.addTab(page, title)
        self.setCurrentIndex(index)

    def add_new_tab(self, page: QWidget):
        title = "a"
        index = self.addTab(page, title)
        self.setCurrentIndex(index)

    def close_tab(self, index):
        # 最後の1枚は閉じないように制限（または全て閉じたら新規タブ作成）
        if self.count() > 1:
            self.removeTab(index)
