from PySide6.QtCore import QObject, Slot

from live_line_builder.ui.models import PerformanceModel
from live_line_builder.ui.views import LiveInfoView


class LiveInfoController(QObject):
    def __init__(
        self,
        main_content_view: LiveInfoView,
        performance_model: PerformanceModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(
            parent,
        )
        self.main_content_view = main_content_view
        self.performance_model = performance_model

        # ライブ情報
        self.main_content_view.show_name.editingFinished.connect(
            self.on_show_name_editingFinished
        )
        self.main_content_view.show_name.setText(self.performance_model.name)

        self.main_content_view.show_place.editingFinished.connect(
            self.on_show_place_editingFinished
        )
        self.main_content_view.show_place.setText(self.performance_model.place)

        self.main_content_view.show_day.editingFinished.connect(
            self.on_show_day_editingFinished
        )
        self.main_content_view.show_day.setText(self.performance_model.day)

        # 担当情報
        self.main_content_view.crew_live_director.editingFinished.connect(
            self.on_crew_live_director_editingFinished
        )
        self.main_content_view.crew_live_director.setText(
            self.performance_model.live_director
        )

        self.main_content_view.crew_sound_director.editingFinished.connect(
            self.on_crew_sound_director_editingFinished
        )
        self.main_content_view.crew_sound_director.setText(
            self.performance_model.sound_director
        )

        self.main_content_view.crew_sound_crews.editingFinished.connect(
            self.on_crew_sound_crew_editingFinished
        )
        self.main_content_view.crew_sound_crews.setText(
            self.performance_model.sound_crews
        )

    # UI側の書き換えを検知してModelに書き込むSlot.
    # バリデーション等もここに置くと良い
    @Slot()
    def on_show_name_editingFinished(self):
        self.performance_model.name = self.main_content_view.show_name.text()

    @Slot()
    def on_show_place_editingFinished(self):
        self.performance_model.place = self.main_content_view.show_place.text()

    @Slot()
    def on_show_day_editingFinished(self):
        self.performance_model.day = self.main_content_view.show_day.text()

    @Slot()
    def on_crew_live_director_editingFinished(self):
        self.performance_model.live_director = (
            self.main_content_view.crew_live_director.text()
        )

    @Slot()
    def on_crew_sound_director_editingFinished(self):
        self.performance_model.sound_director = (
            self.main_content_view.crew_sound_director.text()
        )

    @Slot()
    def on_crew_sound_crew_editingFinished(self):
        self.performance_model.sound_crews = (
            self.main_content_view.crew_sound_crews.text()
        )
