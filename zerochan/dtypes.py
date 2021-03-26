from enum import IntEnum, Enum
from dataclasses import dataclass
from typing import List


@dataclass
class ZeroChanCategory:
    name: str
    image: str
    type: str
    description: str


@dataclass
class ZeroChanImage:
    title: str
    url: str
    height: int  # in px
    width: int  # in px
    kbsize: int  # in KB

    @property
    def size(self):
        return f"{self.height}x{self.width}"

    # TODO: Download method?


@dataclass
class ZeroChanPage:
    images: List[ZeroChanImage]
    page: int
    max_page: int


class PictureSize(IntEnum):
    ALL_SIZES = 0
    BIGGER_AND_BETTER = 1
    BIG_AND_HUGE = 2


class SortBy(str, Enum):
    LAST = "id"
    POPULAR = "fav"
    RANDOM = "random"
