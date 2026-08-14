class EquipmentEntity:
    data: list[list]

    def __init__(self, data: list[list] | None = None) -> None:
        if data is None:
            self.data = []
        else:
            self.data = data

    # リスト代わりの機能を提供
    # 長さを返す
    def __len__(self):
        return len(self.data)

    # self.data無しでできるよう添え字を置き換え
    def __getitem__(self, i: int):
        return self.data[i]


class EquipmentPortEntity:
    data: list[list]

    def __init__(self, data: list[list] | None = None) -> None:
        if data is None:
            self.data = []
        else:
            self.data = data

    # リスト代わりの機能を提供
    # 長さを返す
    def __len__(self):
        return len(self.data)

    # self.data無しでできるよう添え字を置き換え
    def __getitem__(self, i: int):
        return self.data[i]
