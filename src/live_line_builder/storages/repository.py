from pathlib import Path

from live_line_builder.domain.entities import ProjectDataCargo
from live_line_builder.storages.serializer import ProjectSerializer


class ProjectRepository:
    def __init__(self) -> None:
        self._serializer: ProjectSerializer = ProjectSerializer()

    def load_mock(
        self, mock_file_name: str = "full_mock_data.json"
    ) -> ProjectDataCargo:
        """
        AppMockディレクトリ内のモックJSONを読み込む仮コード(開発・テスト用ヘルパー)
        """
        mock_path = Path(__file__).resolve().parent.parent / "app_mock" / mock_file_name
        json_str = mock_path.read_text(encoding="utf-8")
        return self._serializer.load(json_str)

    def load(self, file_path: Path) -> ProjectDataCargo:
        return self._serializer.load(file_path.read_text(encoding="utf-8"))

    def save(
        self,
        equipment_entity,
        equipment_port_entity,
        performance_groups,
        file_path: Path,
    ):
        json_str = self._serializer.dump(
            equipment_entity, equipment_port_entity, performance_groups
        )
        file_path.write_text(json_str, encoding="utf-8")
