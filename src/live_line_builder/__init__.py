import sys

import qdarktheme
from PySide6.QtWidgets import QApplication

from live_line_builder.ui.app_controller import AppController
from live_line_builder.ui.views.main_window import MainWindow


def main():
    # 1. アプリケーションの作成（必須）
    app = QApplication(sys.argv)

    # テーマをセット
    qdarktheme.setup_theme()

    # アプリの管理システムを起動
    _app_controller = AppController.factory_by_mock()
    # 2. ウィジェット（画面パーツ）の作成と設定

    sys.exit(app.exec())

    app.exec()


if __name__ == "__main__":
    main()
