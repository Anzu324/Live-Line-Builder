from .entity import SetListEntity


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
        self.table_panels: list[list[int]] = []
