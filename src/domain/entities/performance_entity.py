class PerformanceEntity:
    """
    各公演ごとの基本情報を保持する
    """

    name: str = "New PerForMance"
    place: str = "視聴覚ホール"
    day: str = ""
    live_director: str = ""
    sound_director: str = ""
    sound_operators: str = ""

    def __init__(self) -> None:
        pass
