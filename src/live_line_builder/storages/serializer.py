from collections import defaultdict
from typing import Any

from live_line_builder.domain.entities import (
    EquipmentDefinition,
    EquipmentPortDefinition,
    PerformanceGroup,
    ProjectDataCargo,
)
from live_line_builder.domain.line_graph.audio_patch import (
    EquipmentID,
    EquipmentInstance,
    NodeType,
    PortDirection,
    PortGender,
    PortID,
    PortInstance,
)
from live_line_builder.storages.schemas import (
    AudioPatchSystemSchema,
    EquipmentPortSchema,
    EquipmentSchema,
    PatchConnectionSchema,
    PatchEquipmentSchema,
    PatchPortSchema,
    PerformanceGroupSchema,
    PerformanceSchema,
    ProjectDataSchema,
)


class ProjectSerializer:
    """プロジェクトデータのシリアライザー。ファイル保存ではなくPythonオブジェクトのエンティティとJSONの変換が責務。

    Entity ➔ Schema(Pydantic) ➔ JSON
    """

    def load(self, json_str: str) -> ProjectDataCargo:
        """JSON(ネスト) ➔ Entity(フラット)"""
        schema = ProjectDataSchema.model_validate_json(json_str)

        equip_rows: list[dict[str, Any]] = []
        port_rows: list[dict[str, Any]] = []

        for equip in schema.equipments:
            # 1. Equipment 本体のデータ (portsを除外してdict化)
            equip_dict: dict[str, Any] = equip.model_dump(exclude={"ports"})
            equip_rows.append(equip_dict)

            # 2. ネストされた ports を展開し、親の equip_id を注入する
            for port in equip.ports:
                port_dict = port.model_dump()
                port_dict["equip_id"] = equip.equip_id  # 🌟 ここで親のIDを付与！
                port_rows.append(port_dict)

        # 3. PerformanceGroup の復元
        performance_groups: list[PerformanceGroup] = []
        for pg_schema in schema.performance_group:
            pg = PerformanceGroup()

            # (1) PerformanceInfoEntity の復元
            info_schema = pg_schema.performance_info
            if info_schema:
                pg._performance_info.tab_name = info_schema.tab_name
                pg._performance_info.name = info_schema.name
                pg._performance_info.place = info_schema.place
                pg._performance_info.day = info_schema.day
                pg._performance_info.live_director = info_schema.live_director
                pg._performance_info.sound_director = info_schema.sound_director
                pg._performance_info.sound_crews = info_schema.sound_crews

            # (2) AudioPatchSystem の復元
            audio_schema = pg_schema.audio_patch
            if audio_schema:
                # 機器とポートの登録
                for eq_schema in audio_schema.equipments:
                    # NodeTypeの変換（大文字小文字や値のマッチング）
                    node_type = None
                    for nt in NodeType:
                        if (
                            nt.value.lower() == eq_schema.equip_type.lower()
                            or nt.name.lower() == eq_schema.equip_type.lower()
                        ):
                            node_type = nt
                            break
                    if node_type is None:
                        node_type = NodeType.INSTRUMENT

                    eq = EquipmentInstance(
                        id=EquipmentID(eq_schema.equip_id),
                        name=eq_schema.name,
                        type=node_type,
                    )
                    pg._audiopatch._add_equipment(eq)

                    for port_schema in eq_schema.ports:
                        direction = (
                            PortDirection.OUT
                            if port_schema.flow.upper() == "OUT"
                            else PortDirection.IN
                        )
                        gender = (
                            PortGender.MALE
                            if direction == PortDirection.OUT
                            else PortGender.FEMALE
                        )
                        audio_port = PortInstance(
                            id=PortID(port_schema.port_id),
                            name=port_schema.name,
                            direction=direction,
                            gender=gender,
                            equipment_id=eq.id,
                        )
                        pg._audiopatch._add_port(audio_port)

                # 結線 (connections) の復元
                for conn in audio_schema.connections:
                    from_id = PortID(conn.from_port_id)
                    to_id = PortID(conn.to_port_id)
                    if (
                        from_id in pg._audiopatch.ports
                        and to_id in pg._audiopatch.ports
                    ):
                        pg._audiopatch.connect_ports(from_id, to_id)

            performance_groups.append(pg)

        return ProjectDataCargo(
            EquipmentDefinition(rows=equip_rows),
            EquipmentPortDefinition(rows=port_rows),
            performance_groups,
        )

    def dump(
        self,
        equip_table: EquipmentDefinition,
        port_table: EquipmentPortDefinition,
        performance_groups: list[PerformanceGroup],
    ) -> str:
        """Entity(フラット) ➔ JSON(ネスト)"""
        # 1. Portデータを equip_id ごとにグループ化しておく
        ports_by_equip = defaultdict(list)
        for port_row in port_table.rows:
            port_data: dict[str, Any] = port_row.model_dump()
            equip_id = port_data.pop("equip_id", None)

            if equip_id:
                ports_by_equip[equip_id].append(
                    EquipmentPortSchema.model_validate(port_data)
                )

        # 2. Equipment と グループ化した Port を結合して Pydantic Schema を作成
        equip_schemas = []
        for equip_row in equip_table.rows:
            equip_data: dict[str, Any] = equip_row.model_dump()
            equip_id = equip_data["equip_id"]

            equip_schema = EquipmentSchema.model_validate(
                {
                    **equip_data,
                    "ports": ports_by_equip.get(
                        equip_id, []
                    ),  # 該当するPortのリストをセット
                }
            )
            equip_schemas.append(equip_schema)

        # 3. PerformanceGroup を Pydantic Schema に変換
        performance_group_schemas: list[PerformanceGroupSchema] = []
        for performance_group in performance_groups:
            # PerformanceSchema
            info = performance_group._performance_info
            info_schema = PerformanceSchema(
                tab_name=info.tab_name,
                name=info.name,
                place=info.place,
                day=info.day,
                live_director=info.live_director,
                sound_director=info.sound_director,
                sound_crews=info.sound_crews,
            )

            # AudioPatchSystemSchema
            patch_ports_by_eq = defaultdict(list)
            for port in performance_group._audiopatch.ports.values():
                patch_ports_by_eq[port.equipment_id].append(
                    PatchPortSchema(
                        port_id=str(port.id),
                        name=port.name,
                        connector="XLR" if port.gender == PortGender.MALE else "XLR-F",
                        flow=port.direction.value,
                    )
                )

            patch_equipments = []
            for equip in performance_group._audiopatch.equipments.values():
                patch_equipments.append(
                    PatchEquipmentSchema(
                        equip_id=str(equip.id),
                        name=equip.name,
                        equip_type=equip.type.value,
                        ports=patch_ports_by_eq.get(equip.id, []),
                    )
                )

            patch_connections = []
            for (
                out_port_id,
                in_port_ids,
            ) in performance_group._audiopatch.forward_edges.items():
                for in_port_id in in_port_ids:
                    patch_connections.append(
                        PatchConnectionSchema(
                            from_port_id=str(out_port_id),
                            to_port_id=str(in_port_id),
                        )
                    )

            audio_schema = AudioPatchSystemSchema(
                equipments=patch_equipments,
                connections=patch_connections,
            )

            performance_group_schemas.append(
                PerformanceGroupSchema(
                    performance_info=info_schema,
                    audio_patch=audio_schema,
                )
            )

        # プロジェクト全体のスキーマにパックしてJSON文字列にして返す
        return ProjectDataSchema(
            equipments=equip_schemas,
            performance_group=performance_group_schemas,
        ).model_dump_json(indent=2)
