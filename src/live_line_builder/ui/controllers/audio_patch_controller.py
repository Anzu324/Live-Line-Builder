from PySide6.QtCore import QObject

from live_line_builder.ui.models import AudioPatchSystemAttributesModel
from live_line_builder.ui.views.audio_patch_view import AudioPatchView


class AudioPatchController(QObject):
    def __init__(
        self, view: AudioPatchView, attributes_model: AudioPatchSystemAttributesModel
    ):
        self._view = view
        self._attributes_model = attributes_model
        self._view.set_combo_items(attributes_model.gateway_equipments_name)

    @property
    def view(self) -> AudioPatchView:
        return self._view
