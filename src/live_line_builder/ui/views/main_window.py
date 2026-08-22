from PySide6.QtWidgets import QPushButton, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from live_line_builder.ui.views.worksheet_view import (
    WorkSheetView,  # メインコンテンツビューをインポート
)


# メインウィンドウのクラス
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # 親ウィジェットなしで初期化

        # ウィンドウサイズを指定（px単位）
        windowWidth = 600  # ウィンドウの横幅
        windowHeight = 500  # ウィンドウの高さ
        self.resize(windowWidth, windowHeight)

        # ウィンドウタイトルを指定
        self.setWindowTitle("LIVE LINE BUILDER")

        self.v_layout = QVBoxLayout(self)  # 垂直方向のレイアウトを作成

        # ウィジェットの作成と配置
        self.button = QPushButton(self)  # ボタンの作成
        self.button.setText("Click Me")  # ボタンのテキストを設定
        self.button.show()

        self.tabs = QTabWidget()

        self.scroll_area = QScrollArea()

        # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
        self.scroll_area.setWidgetResizable(True)

        # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
        self.scroll_area.setMinimumSize(250, 200)
        self.tabs.addTab(self.scroll_area, "1Day")

        self.v_layout.addWidget(self.button)  # レイアウトにボタンを追加
        self.v_layout.addWidget(self.tabs)  # レイアウトにメインコンテンツビューを追加

    def set_central_widget(self, widget: WorkSheetView):
        self.central_widget = widget
        self.scroll_area.setWidget(self.central_widget)

    def set_tab(self, tabs: list[QWidget]):
        self.tabs.clear()
        for i in tabs:
            self.scroll_area = QScrollArea()
            self.tabs.addTab(i, "1Day")
