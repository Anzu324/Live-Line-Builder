from enum import Enum, auto

from .entity import SetListEntity


class TableViewType(Enum):
    SETLIST = auto()
    MULTI = auto()
    MIXER_IN = auto()
    MIXER_OUT = auto()


class TableViewSelector:
    view_type: TableViewType = TableViewType.SETLIST
    id: int  # TODO 実装が定まっていない


class PerformanceEntity:
    """
    各公演ごとの基本情報を保持する
    """

    tab_name: str = "New"
    name: str = "新規公演"
    place: str = "視聴覚ホール"
    day: str = ""
    live_director: str = ""
    sound_director: str = ""
    sound_operators: str = ""

    def __init__(self) -> None:
        self.setlist: SetListEntity = SetListEntity()
        self.table_panels: list[list[TableViewSelector]] = []
