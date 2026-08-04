import sys

from PySide6.QtWidgets import QApplication, QLabel

# 1. アプリケーションの作成（必須）
app = QApplication(sys.argv)

# 2. ウィジェット（画面パーツ）の作成と設定
label = QLabel("Hello World")
label.resize(300, 200)  # 幅300px、高さ200pxに設定

# 3. 画面に表示する
label.show()

# 4. イベントループの開始（ウィンドウを閉じないように保持）
sys.exit(app.exec())
