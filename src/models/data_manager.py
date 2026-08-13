from PySide6.QtCore import QObject


class DataManager(QObject):
    """
    ModelやUIから呼び出され複数のエンティティ(ピュアなデータ)間の橋渡しを担う。
    """

    def __init__(self) -> None:
        pass
