from collections import defaultdict
from pathlib import Path

from live_line_builder.domain.entities import EquipmentEntity, EquipmentPortEntity
from live_line_builder.storages.schemas import (
    EquipmentPortSchema,
    EquipmentSchema,
    ProjectDataSchema,
)


# AIそのまま持ってきた実装(参考用)
class EquipmentRepository:
    def load(self, file_path: Path) -> tuple[EquipmentEntity, EquipmentPortEntity]:
        """JSON(ネスト) ➔ Entity(フラット)"""
        json_str = file_path.read_text(encoding="utf-8")
        schema = ProjectDataSchema.model_validate_json(json_str)

        equip_rows = []
        port_rows = []

        for equip in schema.equipments:
            # 1. Equipment 本体のデータ (portsを除外してdict化)
            equip_dict = equip.model_dump(exclude={"ports"})
            equip_rows.append(equip_dict)

            # 2. ネストされた ports を展開し、親の equip_id を注入する
            for port in equip.ports:
                port_dict = port.model_dump()
                port_dict["equip_id"] = equip.equip_id  # 🌟 ここで親のIDを付与！
                port_rows.append(port_dict)

        return EquipmentEntity(rows=equip_rows), EquipmentPortEntity(rows=port_rows)

    def save(
        self,
        file_path: Path,
        equip_table: EquipmentEntity,
        port_table: EquipmentPortEntity,
    ):
        """Entity(フラット) ➔ JSON(ネスト)"""
        # 1. Portデータを equip_id ごとにグループ化しておく
        ports_by_equip = defaultdict(list)
        for port_row in port_table.rows:
            # Pydantic化する前に equip_id を除去したコピーを作成
            port_data = port_row.copy()
            equip_id = port_data.pop("equip_id", None)

            if equip_id:
                ports_by_equip[equip_id].append(EquipmentPortSchema(**port_data))

        # 2. Equipment と グループ化した Port を結合して Pydantic Schema を作成
        equip_schemas = []
        for equip_row in equip_table.rows:
            equip_id = equip_row["equip_id"]

            equip_schema = EquipmentSchema(
                **equip_row,
                ports=ports_by_equip.get(equip_id, []),  # 該当するPortのリストをセット
            )
            equip_schemas.append(equip_schema)

        # 3. ファイル書き出し
        project_schema = ProjectDataSchema(equipments=equip_schemas)
        file_path.write_text(project_schema.model_dump_json(indent=2), encoding="utf-8")
