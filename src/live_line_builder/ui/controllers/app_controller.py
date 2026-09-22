from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from live_line_builder.app_mock import mock_data
from live_line_builder.domain.entities import ProjectDataEntity
from live_line_builder.domain.line_graph.audio_patch import print_all_connections
from live_line_builder.storages import ProjectRepository
from live_line_builder.ui.controllers import (
    PerformanceTabController,
    PlanSheetController,
)
from live_line_builder.ui.models import (
    DataManager,
    EquipmentModel,
    EquipmentPortModel,
    PerformanceGroupModel,
    PerformanceModel,
)
from live_line_builder.ui.views import AudioPatchTableView, MainWindow, PlanSheetView


# ★ QObject を継承する
class AppController(QObject):
    """main_windowに代わってModel,View,Controllerを生成し組み立て、配線するまでを担当。"""

    # ★ カスタムシグナルの定義（QObject の直下に書く）
    data_changed = Signal()  # 引数なしの通知
    product_added = Signal(dict)  # 追加された商品データ（dict）を飛ばす通知
    _data_mangeger: DataManager

    def __init__(
        self,
        parent=None,
        equipment_list: list[list[str]] | None = None,
        equipment_ports: list[list[str]] | None = None,
    ):
        # 親クラスのQObjectのご加護を得る
        super().__init__(parent)

        self.project_datum = ProjectDataEntity()  # XXX:いつかはDataManagerに任せる。

        self._data_mangeger = DataManager(
            self, equipment_list=equipment_list, equipment_ports=equipment_ports
        )

        # HACK: モックをここで読み込んで使用しております。
        self.load_mock_project()

        self.performance_data = [
            PerformanceModel(self, i._performance_info)
            for i in self._data_mangeger._performance_group_list
        ]

        # DEBAG:コンソールに読み込んだパッチの接続状況を書き出すコード。
        print("Talk by AppController")
        for i in self._data_mangeger._performance_group_list:
            print_all_connections(i._audiopatch)

        # 文字列で機器表を初期化する
        self._equipments = EquipmentModel(self._data_mangeger.equipment_entity)

        # 文字列でコネクター表を初期化する。
        self._equipment_ports = EquipmentPortModel(
            self._data_mangeger.equipment_port_entity
        )

        self.main_window = (
            MainWindow()
        )  # selfをつけ生存期間をAppCOntorollerと同等に延長
        self.main_window.set_window_title(
            self.project_datum.file_name
        )  # XXX:ここに書くの良くないね。

        self.set_menubar()

        self.main_window.show()  # 表示

        tab_names: list[str] = []

        self.worksheet_widgets: list[PlanSheetView] = []
        self.worksheet_ctrls: list[PlanSheetController] = []
        self.patch_views: list[QWidget] = []
        for model in self.performance_data:
            view = PlanSheetView(
                self._equipments,
                self._equipment_ports,
                [1, 2],  # 例: 列0と列1をフィルター対象とする
                parent=self.main_window,
            )
            self.worksheet_widgets.append(view)
            self.worksheet_ctrls.append(PlanSheetController(view, model))
            self.patch_views.append(
                AudioPatchTableView()
            )  # 仮で同じviewを追加しているだけです。
            tab_names.append(model.tab_name)

        PerformanceTabController(
            self.main_window.tabs,
            PerformanceGroupModel(group=self._data_mangeger._performance_group_list),
        ).set_tabs(list(zip(tab_names, self.worksheet_widgets, self.patch_views)))

    def load_mock_project(self, mock_file_name: str = "full_mock_data.json"):
        """開発用のモックJSONを読み込んでプロジェクトを立ち上げる"""
        repository = ProjectRepository()
        cargo = repository.load_mock(mock_file_name)
        self._data_mangeger.load_by_cargo(cargo)

    # モックでデータマネージャーを構築する
    @staticmethod
    def factory_by_mock() -> AppController:
        print("悪いfactoryを呼んでいる。早めに移行せよ")
        return AppController(None, mock_data.equipment_data, mock_data.port_data)

    @Slot()
    def change_performance(self):
        """公演を切り替える"""

    @property
    def data_mangeger(self):
        return self._data_mangeger

    # def add_product(self, product_data: dict):
    #     """商品追加と同時にシグナルを発火する"""
    #     self._products.append(product_data)

    #     # ★ シグナルを発火（通知）！
    #     self.product_added.emit(product_data)
    #     self.data_changed.emit()

    def set_menubar(self) -> None:
        menu_bar = self.main_window.menuBar()

        # --- 1. 階層構造（サブメニュー）の作成 ---
        file_menu = menu_bar.addMenu("ファイル(&F)")

        file_menu.addAction(QAction("新規空オブジェクト(&N)", self))

        # QMenuオブジェクトに対して addMenu() を呼ぶことでネスト可能
        export_menu = file_menu.addMenu("エクスポート(&E)")
        export_menu.addAction(QAction("PDF形式...(&P)", self))
        export_menu.addAction(QAction("PNG画像...(&I)", self))

        file_menu.addSeparator()

        exit_action = QAction("終了(&X)", self)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)

        # --- 2. チェックボックス付きQActionの作成 ---
        view_menu = menu_bar.addMenu("表示(&V)")

        # setCheckable(True) でチェック可能にする
        grid_action = QAction("グリッドを表示(&G)", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)  # 初期状態をオンに設定

        # toggled シグナルはチェック状態の変更時(bool)を通知する
        grid_action.toggled.connect(self.on_grid_toggled)

        view_menu.addAction(grid_action)

    def on_grid_toggled(self, checked: bool):
        status = "有効" if checked else "無効"
        print(f"グリッド表示: {status}")
