"""AIが作った参考用のUI実装コード。

サブメニューの開閉を行う部分を実装してもらいました。
"""

import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("スライド開閉パネル（確実版）")
        self.resize(600, 400)

        # メインのウィジェットとレイアウト
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. 左側のサイドパネル ---
        self.side_panel = QFrame()
        self.side_panel.setObjectName("SidePanel")
        self.side_panel.setStyleSheet("#SidePanel { background-color: #2c3e50; }")

        # 最小幅は0にしておき、初期の最大幅を200（開いた状態）にします
        self.side_panel.setMinimumWidth(0)
        self.side_panel.setMaximumWidth(200)

        # サイドパネルの中身
        panel_layout = QVBoxLayout(self.side_panel)
        panel_label = QLabel("サイドメニュー")
        panel_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        panel_layout.addWidget(panel_label)
        panel_layout.addStretch()

        # --- 2. 右側のメインコンテンツエリア ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # パネルを開閉するためのボタン
        self.toggle_button = QPushButton("メニューを開閉")
        self.toggle_button.clicked.connect(self.toggle_panel)

        content_layout.addWidget(self.toggle_button)
        content_layout.addWidget(QLabel("ここにメインの画面コンテンツが入ります。"))
        content_layout.addStretch()

        # レイアウトに各エリアを追加
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(content_widget)

        # --- 3. アニメーションの設定 ---
        # maximumWidthをアニメーションさせることで、幅が0〜200の間で滑らかに変わります
        self.animation = QPropertyAnimation(self.side_panel, b"maximumWidth")
        self.animation.setDuration(250)  # アニメーションの時間（ミリ秒）
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # パネルの状態管理フラグ（True = 開いている, False = 閉じている）
        self.is_panel_open = True

    def toggle_panel(self):
        """パネルの開閉を切り替えるメソッド"""
        # アニメーション中はボタン連打を無効化する
        if self.animation.state() == QPropertyAnimation.State.Running:
            return

        if self.is_panel_open:
            # 閉じる：200から0へ
            self.animation.setStartValue(200)
            self.animation.setEndValue(0)
            self.animation.start()
            self.is_panel_open = False
        else:
            # 開く：0から200へ
            self.animation.setStartValue(0)
            self.animation.setEndValue(200)
            self.animation.start()
            self.is_panel_open = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
