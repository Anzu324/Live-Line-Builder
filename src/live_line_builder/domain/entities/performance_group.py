from live_line_builder.domain.entities.performance_info_entity import (
    PerformanceInfoEntity,
)
from live_line_builder.domain.line_graph.audio_patch import AudioPatchSystem


class PerformanceGroup:
    """
    公演ごとに分けてデータを持つ機能
    """

    def __init__(self) -> None:
        self._performance_info: PerformanceInfoEntity = PerformanceInfoEntity()
        self._audiopath: AudioPatchSystem = AudioPatchSystem()

    @staticmethod
    def make_default() -> PerformanceGroup:
        """
        __init__が変更されても常に引数無しで初期値が生成することを保証する。
        """
        return PerformanceGroup()
