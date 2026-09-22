import zipfile
from pathlib import Path


class ProjectZipStorage:
    def __init__(self, zip_path: Path):
        self.zip_path = zip_path

    def write_files_to_zip(self, files: list[Path]):
        with zipfile.ZipFile(self.zip_path, "w") as zipf:
            for file in files:
                zipf.write(file)
