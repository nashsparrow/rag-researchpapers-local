from dataclasses import dataclass

@dataclass
class JSONFileData:
    file_id: str = None
    filename: str = None
    pagenumber: int = None
    text: str = None