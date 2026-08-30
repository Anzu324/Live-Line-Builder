from PySide6.QtWidgets import QFormLayout, QGridLayout, QLineEdit, QWidget


# メインコンテンツビューのクラス
# メインコンテンツビューとは、中央にある、図や表を表示する為のウィジェットです。
class LiveInfoView(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        # ライブ情報エリア
        self.grid_layout = QGridLayout()
        self.show_form_Layout = QFormLayout()
        self.show_name = QLineEdit()
        self.show_place = QLineEdit()
        self.show_day = QLineEdit()
        self.show_form_Layout.addRow(self.tr("公演名"), self.show_name)
        self.show_form_Layout.addRow(self.tr("開場"), self.show_place)
        self.show_form_Layout.addRow(self.tr("日時"), self.show_day)

        self.crew_form_Layout = QFormLayout()
        self.crew_stage_director = QLineEdit()
        self.crew_sound_director = QLineEdit()
        self.crew_sound_crew = QLineEdit()
        self.crew_form_Layout.addRow(self.tr("舞台監督"), self.crew_stage_director)
        self.crew_form_Layout.addRow(self.tr("音響監督"), self.crew_sound_director)
        self.crew_form_Layout.addRow(self.tr("音響"), self.crew_sound_crew)

        self.show_form_Layout.setContentsMargins(0, 0, 0, 0)
        self.show_form_Layout.setSpacing(5)  # レイアウトの余白を5に設定
        self.crew_form_Layout.setContentsMargins(0, 0, 0, 0)
        self.crew_form_Layout.setSpacing(5)  # レイアウトの余白を5に設定
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)

        self.grid_layout.addLayout(self.show_form_Layout, 0, 0)
        self.grid_layout.addLayout(self.crew_form_Layout, 0, 1)
        self.setLayout(self.grid_layout)
