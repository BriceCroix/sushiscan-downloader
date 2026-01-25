from dataclasses import dataclass, field
from typing import List


@dataclass
class Page:
    url: str
    filename: str


@dataclass
class Chapter:
    id: str
    url: str
    title: str = ""
    pages: List[Page] = field(default_factory=list)


@dataclass
class Manga:
    title: str
    url: str
    chapters: List[Chapter] = field(default_factory=list)
