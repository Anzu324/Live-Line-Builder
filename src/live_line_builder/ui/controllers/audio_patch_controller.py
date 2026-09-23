from PySide6.QtCore import QObject

from live_line_builder.ui.views.audio_patch_view import AudioPatchView


class AudioPatchController(QObject):
    def __init__(self, view: AudioPatchView, equip_list: list[str]):
        self._view = view
        self._equip_list = equip_list
        self._view.set_combo_items(equip_list)

    @property
    def view(self) -> AudioPatchView:
        return self._view
