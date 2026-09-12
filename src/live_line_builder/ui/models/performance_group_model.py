from live_line_builder.domain.entities import PerformanceGroup
from live_line_builder.ui.models.project_data_model import PerformanceModel


class PerformanceGroupModel:
    def __init__(self, group: PerformanceGroup) -> None:
        self._group: PerformanceGroup = group

    def get_performace_info_model(self) -> PerformanceModel:
        return PerformanceModel(entity=self._group._performance_info)
