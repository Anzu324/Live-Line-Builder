from PySide6.QtCore import QObject, Slot

from live_line_builder.ui.models import (
    AudioPatchSystemAttributesModel,
    PatchTableModel,
    Stream,
)
from live_line_builder.ui.views.audio_patch_view import AudioPatchView


class AudioPatchController(QObject):
    def __init__(
        self,
        view: AudioPatchView,
        attributes_model: AudioPatchSystemAttributesModel,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._view = view
        self._attributes_model = attributes_model
        self._table_model = PatchTableModel(
            attributes_model.get_raw_entity, Stream.INPUT, parent=self
        )
        self._view.set_combo_items(attributes_model.gateway_equipments_name)
        self._view.table.setModel(self._table_model)
        self._view.combo.currentIndexChanged.connect(self.on_equipment_selected)
        self.on_equipment_selected(self._view.combo.currentIndex())

    @property
    def view(self) -> AudioPatchView:
        return self._view

    @Slot()
    def on_equipment_selected(self, index: int):
        if index < 0:
            return
        equipment = self._attributes_model.gateway_equipments[index].id
        self._table_model.change_base_point(equipment, Stream.INPUT)
