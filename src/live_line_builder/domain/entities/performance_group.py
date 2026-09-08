from live_line_builder.domain.entities import PerformanceEntity
from live_line_builder.domain.line_graph.audio_patch import AudioPatchSystem


class PerformanceGroup:
    """
    公演ごとに分けてデータを持つ機能
    """

    def __init__(self) -> None:
        self._live_info: PerformanceEntity = PerformanceEntity()
        self._audiopath: AudioPatchSystem = AudioPatchSystem()

    @staticmethod
    def make_default() -> PerformanceGroup:
        """
        __init__が変更されても常に引数無しで初期値が生成することを保証する。
        """
        return PerformanceGroup()
