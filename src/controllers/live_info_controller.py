from PySide6.QtCore import QObject, Slot

from models import PerformanceModel
from views import LiveInfoView


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

        self.main_content_view.show_name.editingFinished.connect(
            self.on_show_name_editingFinished
        )
        self.main_content_view.show_place.editingFinished.connect(
            self.on_show_place_editingFinished
        )
        self.main_content_view.show_day.editingFinished.connect(
            self.on_show_day_editingFinished
        )

    @Slot()
    def on_show_name_editingFinished(self):
        print("Umakuitteru")
        self.performance_model.name = self.main_content_view.show_name.text()

    @Slot()
    def on_show_place_editingFinished(self):
        self.performance_model.place = self.main_content_view.show_place.text()

    @Slot()
    def on_show_day_editingFinished(self):
        self.performance_model.day = self.main_content_view.show_day.text()
