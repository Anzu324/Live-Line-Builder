from pydantic import BaseModel


class PartSchema(BaseModel):
    part_id: str
    name: str
