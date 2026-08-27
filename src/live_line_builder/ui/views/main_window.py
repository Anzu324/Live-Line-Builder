from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

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
        self.tabs.setContentsMargins(0, 0, 0, 0)

        self.v_layout.addWidget(self.button)  # レイアウトにボタンを追加
        self.v_layout.addWidget(self.tabs)  # レイアウトにメインコンテンツビューを追加

    def set_central_widget(self, widget: WorkSheetView):
        self.set_tabs([widget])
        # self.scroll_area.setWidget(self.central_widget)

    def set_tabs(self, tabs_source: list[WorkSheetView], tab_names=None):
        self.tabs.clear()
        if tab_names is None:
            tab_names = ["" for i in tabs_source]
        for i, j in zip(tabs_source, tab_names):
            scroll_area = QScrollArea()
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
            # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
            scroll_area.setWidgetResizable(True)
            # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
            scroll_area.setMinimumSize(250, 200)

            scroll_area.setWidget(i)
            self.tabs.addTab(scroll_area, j)
