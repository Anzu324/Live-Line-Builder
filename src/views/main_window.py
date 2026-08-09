from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from mock.mock_data import connector_data, equipment_data  # モックデータをインポート
from models.equipment_table import (  # モデルをインポート
    EquipmentConnectorModel,
    EquipmentModel,
)
from views.main_content_view import (
    MainContentView,  # メインコンテンツビューをインポート
)


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
        self.label.resize(100, 50)  # 幅100px、高さ100pxに設定
        self.label.show()
        # self.label.move(50, 50)  # ラベルの位置を指定（左上からの座標）

        self.button = QPushButton(self)  # ボタンの作成
        self.button.setText("Click Me")  # ボタンのテキストを設定
        self.button.resize(100, 100)  # 幅100px、高さ50pxに設定
        self.button.show()
        # self.button.move(50, 250)  # ボタンの位置を指定（左上からの座標）

        # EquipmentModelのインスタンスを作成
        self.equipment_data = EquipmentModel(equipment_data)  # モックデータを渡す

        # コネクタのデータを保持するEquipmentConnectorModelのインスタンスを作成
        self.connector_data = EquipmentConnectorModel(
            connector_data
        )  # モックデータを渡す

        self.central_widget = MainContentView(
            self.equipment_data,
            self.connector_data,
            [1, 2],  # 例: 列0と列1をフィルター対象とする
        )  # メインコンテンツビューの作成

        self.v_layout.addWidget(self.label)  # レイアウトにラベルを追加
        self.v_layout.addWidget(self.button)  # レイアウトにボタンを追加
        self.v_layout.addWidget(
            self.central_widget
        )  # レイアウトにメインコンテンツビューを追加
