import sys

import qdarktheme
from PySide6.QtWidgets import QApplication

from ui.views.main_window import MainWindow

# 1. アプリケーションの作成（必須）
app = QApplication(sys.argv)

qdarktheme.setup_theme()
# 2. ウィジェット（画面パーツ）の作成と設定
main_window = MainWindow()
main_window.show()

sys.exit(app.exec())

app.exec()
