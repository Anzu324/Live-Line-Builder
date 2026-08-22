from pydantic import BaseModel


class EquipmentSchema(BaseModel):
    equip_id: str
    name: str
    equip_type: str
    quantity: int
    ports_list: list[EquipmentPortSchema]


class EquipmentPortSchema(BaseModel):
    port_id: str
    name: str
    connerctor: str
    flow: str


class ProjectDataSchema(BaseModel):
    parts: list[EquipmentSchema] = []

    # def to_part_table(self) -> PartTableEntity:
    #     # SchemaがEntityを生成して返す
    #     return PartTableEntity(rows=[p.model_dump() for p in self.parts])
