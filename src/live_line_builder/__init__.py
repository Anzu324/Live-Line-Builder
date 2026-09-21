import faulthandler
import sys

import qdarktheme
from PySide6.QtWidgets import QApplication

from live_line_builder.theme import setup_theme
from live_line_builder.ui.controllers.app_controller import AppController
from live_line_builder.ui.views.main_window import MainWindow


def main():

    faulthandler.enable()  # コードの最初（sys.exitの前など）で実行

    # 1. アプリケーションの作成（必須）
    app = QApplication(sys.argv)

    setup_theme()

    # アプリの管理システムを起動
    _app_controller = AppController.factory_by_mock()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
