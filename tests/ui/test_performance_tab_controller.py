from PySide6.QtWidgets import QWidget

from live_line_builder.domain.entities.performance_group import PerformanceGroup
from live_line_builder.ui.controllers.performance_tab_controller import (
    PerformanceTabController,
)
from live_line_builder.ui.models.performance_group_model import PerformanceGroupModel
from live_line_builder.ui.views.tabs import WorkSheetTabWidget


def test_set_tabs_creates_one_tab_per_group(qapp):
    groups = [PerformanceGroup.make_default(), PerformanceGroup.make_default()]
    model = PerformanceGroupModel(group=groups)
    view = WorkSheetTabWidget()
    controller = PerformanceTabController(view=view, performance_group=model)

    tabs = [
        ("Tab 1", QWidget(), QWidget()),
        ("Tab 2", QWidget(), QWidget()),
    ]

    controller.set_tabs(tabs)

    assert view.count() == len(tabs)
    assert view.tabText(0) == "Tab 1"
    assert view.tabText(1) == "Tab 2"
