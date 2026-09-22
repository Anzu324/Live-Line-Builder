from dataclasses import dataclass

from live_line_builder.domain.entities.entity import (
    EquipmentDefinition,
    EquipmentPortDefinition,
)
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
        self._audiopatch: AudioPatchSystem = AudioPatchSystem()

    @staticmethod
    def make_default() -> PerformanceGroup:
        """
        __init__が変更されても常に引数無しで初期値が生成することを保証する。
        """
        return PerformanceGroup()

    def __repr__(self) -> str:
        return f"PerformanceGroup({self._performance_info!r}, {self._audiopatch!r})"


@dataclass
class ProjectDataCargo:
    equipment_entity: EquipmentDefinition
    equipment_port_entity: EquipmentPortDefinition
    performance_group_list: list[PerformanceGroup]
