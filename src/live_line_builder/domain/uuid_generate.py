import uuid
from uuid import UUID

# テスト時のuuid5用
MY_SYSTEM_NAMESPACE = uuid.UUID("d1adda42-a1b6-42aa-8079-e29d564ce382")


def generate_uuid4() -> UUID:
    """
    本番用IDをUUID4で生成
    """
    return uuid.uuid4()


def generate_uuid5(munual_id: str) -> UUID:
    """
    テスト用
    自作のIDをUUIDに自動変換する
    """
    return uuid.uuid5(MY_SYSTEM_NAMESPACE, munual_id)
