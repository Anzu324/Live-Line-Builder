from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class GroundPlanView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. 画像を表示するためのQLabel
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # 中央揃えに設定

        # 💡 初期状態（画像がない時）のテキストを設定
        # 改行を入れて、左下のボタンの位置を避ける案内文にします
        self.image_label.setText(
            "舞台図が登録されていません。\n"
            "左下の「＋」ボタンから画像を追加してください。"
        )
        # スタイルシートで文字を薄いグレーにして「未登録感」を出す
        self.image_label.setStyleSheet("color: #757575; font-size: 14px; font-weight: bold;")

        # ボタンの配置用マージンとサイズ
        self.button_margin = 15
        button_size = 30

        # メインレイアウト
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.image_label)

        # 画像がない状態でも、ある程度の「表示領域」を確保するために最小サイズを設定
        # これにより、QScrollArea の中で極端に潰れるのを防ぎます
        self.image_label.setMinimumSize(240, 180)

        # 画像の下（文字の下）に、ボタンが絶対に被らないためのスペースを空ける
        extra_space = button_size + (self.button_margin * 2)
        self.main_layout.addSpacing(extra_space)

        self.setLayout(self.main_layout)

        # 2. 左下に重ねる小さな丸いボタン
        self.overlay_button = QPushButton("＋", self)
        self.overlay_button.setFixedSize(button_size, button_size)

        self.overlay_button.setObjectName("overlayAddButton")

    # 🔗 画像を設定するための外部呼び出し用メソッド
    def set_image(self, file_path: str):
        """外部から画像をセットする関数"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # テキストのスタイルをクリアして画像をセット
            self.image_label.setStyleSheet("")
            self.image_label.setPixmap(pixmap)

            # 画像のサイズに応じて QLabel の最小サイズを画像サイズに合わせる
            # これにより、画像読み込み後はスクロールバーが正常に機能します
            self.image_label.setMinimumSize(pixmap.size())
            self.image_label.adjustSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = self.width() - self.overlay_button.width() - self.button_margin
        y = self.height() - self.overlay_button.height() - self.button_margin
        self.overlay_button.move(x, y)
        self.overlay_button.raise_()
