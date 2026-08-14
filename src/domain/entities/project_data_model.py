class ProjectDataModel:
    """
    プロジェクト(ファイル)ごとの情報を保持する。
    ファイル名や保存パスなど。保存時は加工が必要かも?
    """

    file_name: str = "New Project"
    file_path: str = ""
