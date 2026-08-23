from PySide6.QtCore import QObject, Signal

from live_line_builder.domain.entities import PerformanceEntity


class PerformanceModel(QObject):
    """
    ライブの各"公演"情報を保持するモデル。
    """

    data_changed = Signal()  # 引数なしの通知

    def __init__(self, parent=None, entity: PerformanceEntity | None = None) -> None:
        super().__init__(parent)
        if entity is None:
            self._performance = PerformanceEntity()
        else:
            self._performance = entity

    @property
    def name(self) -> str:
        return self._performance.name

    @name.setter
    def name(self, value: str) -> None:
        self._performance.name = value
        self.data_changed.emit()

    @property
    def place(self) -> str:
        return self._performance.place

    @place.setter
    def place(self, value: str) -> None:
        self._performance.place = value
        self.data_changed.emit()

    @property
    def day(self) -> str:
        return self._performance.day

    @day.setter
    def day(self, value: str) -> None:
        self._performance.day = value
        self.data_changed.emit()

    @property
    def live_director(self) -> str:
        return self._performance.live_director

    @live_director.setter
    def live_director(self, value: str) -> None:
        self._performance.live_director = value
        self.data_changed.emit()

    @property
    def sound_director(self) -> str:
        return self._performance.sound_director

    @sound_director.setter
    def sound_director(self, value: str) -> None:
        self._performance.sound_director = value
        self.data_changed.emit()

    @property
    def sound_operators(self) -> str:
        return self._performance.sound_operators

    @sound_operators.setter
    def sound_operators(self, value: str) -> None:
        self._performance.sound_operators = value
        self.data_changed.emit()
