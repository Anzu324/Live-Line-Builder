from live_line_builder.domain.entities import PerformanceGroup
from live_line_builder.ui.models.project_data_model import PerformanceModel


class PerformanceGroupModel:
    def __init__(self, group: list[PerformanceGroup]) -> None:
        self._groups: list[PerformanceGroup] = group

    def get_performace_info_models(self) -> list[PerformanceModel]:
        return [PerformanceModel(entity=i._performance_info) for i in self._groups]

    def get_performace_info_model(self, index: int) -> PerformanceModel:
        return PerformanceModel(entity=self._groups[index]._performance_info)
