from pydantic import BaseModel

# ======= Profiles =======


class EquipmentSchema(BaseModel):
    equip_id: str
    name: str
    equip_type: str
    quantity: int
    ports: list[EquipmentPortSchema]


class EquipmentPortSchema(BaseModel):
    port_id: str
    name: str
    connector: str
    flow: str


# ======= Patch System =======


class PatchPortSchema(BaseModel):
    port_id: str
    name: str
    connector: str
    flow: str


class PatchEquipmentSchema(BaseModel):
    """
    パッチシステムの機器を表すスキーマ
    ここでは、機器のID、名前、タイプ、数量、および接続されているポートのリストを含む。
    PortもEquipment内に保持する。
    """

    equip_id: str
    name: str
    equip_type: str
    quantity: int
    ports: list[PatchPortSchema]


class PatchConnectionSchema(BaseModel):
    """
    パッチ接続を表すスキーマ
    from_port_id:上流から
    to_port_id:下流への接続を表す
    """

    from_port_id: str
    to_port_id: str


class AudioPatchSystemSchema(BaseModel):
    equipments: list[PatchEquipmentSchema] = []
    connections: list[PatchConnectionSchema] = []


# ======= Performance =======


class PerformanceSchema(BaseModel):
    tab_name: str
    name: str
    place: str
    day: str
    live_director: str
    sound_director: str
    sound_crews: str


class PerformanceGroupSchema(BaseModel):
    """
    公演ごとの情報をまとめて持つコンテナ
    """

    performance_data: PerformanceSchema
    patch_system: AudioPatchSystemSchema = AudioPatchSystemSchema()


class ProjectDataSchema(BaseModel):
    equipments: list[EquipmentSchema] = []
    performance_group: list[PerformanceGroupSchema] = []
    # def to_part_table(self) -> PartTableEntity:
    #     # SchemaがEntityを生成して返す
    #     return PartTableEntity(rows=[p.model_dump() for p in self.parts])
