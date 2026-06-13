from dataclasses import dataclass, field, asdict
from typing import List
import json

@dataclass
class JSONPageData:
    pagenumber: int = None
    text: str = None

@dataclass
class JSONChunkData:
    chunk_id: str = None
    chunk_index: int = None
    page_number: int = None
    text: str = None
    char_count: int = None


@dataclass
class JSONFileData:
    file_id: str = None
    filename: str = None
    pages: List[JSONPageData] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

@dataclass
class ChunkedJSONFileData:
    file_id: str = None
    filename: str = None
    chunks: List[JSONChunkData] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


@dataclass
class FlattenedChunkedJSONFileData:
    file_id: str = None
    filename: str = None
    chunk_id: str = None
    chunk_index: int = None
    page_number: int = None
    text: str = None
    char_count: int = None

    def to_dict(self):
        return asdict(self)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

@dataclass
class FlattenedChunkedAndEmbeddedJSONFileData:
    file_id: str = None
    filename: str = None
    chunk_id: str = None
    chunk_index: int = None
    page_number: int = None
    text: str = None
    char_count: int = None
    embedding: List[float] = field(default_factory=list)
