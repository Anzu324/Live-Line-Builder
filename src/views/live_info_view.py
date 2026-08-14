from PySide6.QtWidgets import QFormLayout, QLineEdit, QWidget


# メインコンテンツビューのクラス
# メインコンテンツビューとは、中央にある、図や表を表示する為のウィジェットです。
class LiveInfoView(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        # ライブ情報エリア
        self.formLayout = QFormLayout()
        self.show_name = QLineEdit()
        self.show_place = QLineEdit()
        self.show_day = QLineEdit()
        self.formLayout.addRow(self.tr("公演名"), self.show_name)
        self.formLayout.addRow(self.tr("開場"), self.show_place)
        self.formLayout.addRow(self.tr("日時"), self.show_day)

        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(5)  # レイアウトの余白を10に設定
        self.setLayout(self.formLayout)  # 垂直レイアウトに水平レイアウトを追
