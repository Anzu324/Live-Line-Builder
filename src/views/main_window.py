from PySide6.QtWidgets import QLabel, QPushButton, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # 親ウィジェットなしで初期化

        # ウィンドウサイズを指定（px単位）
        windowWidth = 500  # ウィンドウの横幅
        windowHeight = 400  # ウィンドウの高さ
        self.resize(windowWidth, windowHeight)

        # ウィンドウタイトルを指定
        self.setWindowTitle("LIVE LINE BUILDER")

        # ウィジェットの作成と配置
        self.label = QLabel(self)
        self.label.setText("Hello World")  # ラベルのテキストを設定
        self.label.resize(100, 50)  # 幅100px、高さ100pxに設定
        self.label.show()
        self.label.move(50, 50)  # ラベルの位置を指定（左上からの座標）

        self.button = QPushButton(self)
        self.button.setText("Click Me")  # ボタンのテキストを設定
        self.button.resize(100, 100)  # 幅100px、高さ50pxに設定
        self.button.show()
        self.button.move(50, 250)  # ボタンの位置を指定（左上からの座標）
