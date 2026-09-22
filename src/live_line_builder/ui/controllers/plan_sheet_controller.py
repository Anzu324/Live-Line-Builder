from live_line_builder.ui.models import PerformanceModel
from live_line_builder.ui.views import LiveInfoView, PlanSheetView

from .live_info_controller import LiveInfoController


class PlanSheetController:
    def __init__(self, view: PlanSheetView, live_info_model: PerformanceModel) -> None:
        self._view = view

        live_info_view = LiveInfoView()
        self._live_info_cntl = LiveInfoController(live_info_view, live_info_model)
        self._view.replace_form(live_info_view)

    @property
    def view(self) -> PlanSheetView:
        return self._view
