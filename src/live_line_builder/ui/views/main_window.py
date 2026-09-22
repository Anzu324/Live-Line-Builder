from PySide6.QtWidgets import QFrame, QMainWindow, QScrollArea, QVBoxLayout

from live_line_builder.ui.views.plan_sheet_view import (
    PlanSheetView,  # メインコンテンツビューをインポート
)
from live_line_builder.ui.views.tabs import WorkSheetTabWidget


# メインウィンドウのクラス
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # 親ウィジェットなしで初期化

        # ウィンドウサイズを指定（px単位）
        windowWidth = 600  # ウィンドウの横幅
        windowHeight = 500  # ウィンドウの高さ
        self.resize(windowWidth, windowHeight)

        # ウィンドウタイトルを指定
        self.setWindowTitle("LIVE LINE BUILDER")

        self.v_layout = QVBoxLayout(self)  # 垂直方向のレイアウトを作成

        self.tabs = WorkSheetTabWidget(self)
        self.tabs.setContentsMargins(0, 0, 0, 0)

        self.v_layout.addWidget(self.tabs)  # レイアウトにメインコンテンツビューを追加
        self.setCentralWidget(self.tabs)

    def set_central_widget(self, widget: PlanSheetView):
        self.set_tabs([widget])
        # self.scroll_area.setWidget(self.central_widget)

    def set_tabs(self, tabs_source: list[PlanSheetView], tab_names=None):
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

    def set_window_title(self, projectname: str):
        title = f"LIVE LINE BUILDER - {projectname}"
        self.setWindowTitle(title)
