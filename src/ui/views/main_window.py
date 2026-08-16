from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from ui.views.main_content_view import (
    MainContentView,  # メインコンテンツビューをインポート
)

from .app_controller import AppController  # モデルをインポート


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
        self.label = QLabel(self)
        self.label.setText("Hello World")  # ラベルのテキストを設定
        self.label.show()

        self.button = QPushButton(self)  # ボタンの作成
        self.button.setText("Click Me")  # ボタンのテキストを設定
        self.button.show()

        scroll_area = QScrollArea()

        # 中身のウィジェットをスクロールエリアの幅に自動フィットさせる
        scroll_area.setWidgetResizable(True)

        # 【オプション】潰れすぎ防止：最低でも「幅250px / 高さ200px」は確保する
        scroll_area.setMinimumSize(250, 200)

        # ----------------------------------
        # データマネージャーを用意
        # ----------------------------------
        self.data_manager = AppController.factory_by_mock()

        # EquipmentModelのインスタンスを作成
        equipment_data = self.data_manager.equipments

        # コネクタのデータを保持するEquipmentConnectorModelのインスタンスを作成
        connector_data = self.data_manager.equipment_ports

        self.central_widget = MainContentView(
            equipment_data,
            connector_data,
            [1, 2],  # 例: 列0と列1をフィルター対象とする
        )  # メインコンテンツビューの作成
        scroll_area.setWidget(self.central_widget)

        self.v_layout.addWidget(self.label)  # レイアウトにラベルを追加
        self.v_layout.addWidget(self.button)  # レイアウトにボタンを追加
        self.v_layout.addWidget(scroll_area)  # レイアウトにメインコンテンツビューを追加
