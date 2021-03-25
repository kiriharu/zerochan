from typing import List

import requests
from bs4 import BeautifulSoup
import json

from zerochan.types import (
    PictureSize, ZeroChanCategory,
    ZeroChanImage, ZeroChanPage, SortBy
)
from zerochan.exceptions import NoPicturesFound


class ZeroChan:
    WEBSITE_URL = "https://www.zerochan.net"

    # TODO: filter by image size by pixel, alt and other

    def __init__(self):
        self._tag = ""
        self.cookies = dict(
            z_lang="en"
        )
        self.req_args = {}

    def size(self, size: PictureSize) -> 'ZeroChan':
        self.req_args.update(dict(d=int(size)))
        return self

    def sort(self, sort_by: SortBy) -> 'ZeroChan':
        self.req_args.update(dict(s=sort_by))
        return self

    def page(self, page_num: int) -> 'ZeroChan':
        self.req_args.update(dict(p=page_num))
        return self

    def tag(self, title: str):
        self._tag = title
        return self

    def authorize(self, z_hash: str, z_id: str):
        self.cookies.update(dict(
            z_hash=z_hash,
            z_id=z_id
        ))
        return self

    def _parse_category(self, soup) -> ZeroChanCategory:
        page_data = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))
        menu = soup.find("div", dict(id="menu"))
        # parsing description
        p_tags = menu.find_all("p")
        description = p_tags[1].text.replace("\r\n", "")
        return ZeroChanCategory(
            name=page_data.get("name"),
            image=page_data.get("image"),
            type=page_data.get("@type"),
            description=description
        )

    def _parse_pics(self, pics_soup) -> List[ZeroChanImage]:
        images = []
        for pic in pics_soup.find_all("li"):

            title = pic.img.get("title")
            splitted_title = title.split(" ")
            size = int(splitted_title[1][:-2])  # remove "kb" chars
            height, width = map(int, list(splitted_title[0].split("x")))  # split by x and convert to int

            pic_download_el = pic.p.a
            if pic_download_el.img:
                download_url = pic.p.a.get("href")
            else:
                download_el = pic_download_el.parent.find_all("a")[1]
                download_url = download_el.get("href")
            images.append(
                ZeroChanImage(title=title, url=download_url, height=height, width=width, kbsize=size)
            )
        return images

    def parse(self) -> ZeroChanPage:
        req = requests.get(
            f"{self.WEBSITE_URL}/{self._tag}",
            params=self.req_args,
            cookies=self.cookies
        )
        soup = BeautifulSoup(req.content)
        category = self._parse_category(soup)
        pics_soup = soup.find("ul", dict(id="thumbs2"))
        if pics_soup is None:
            raise NoPicturesFound
        imgs = self._parse_pics(pics_soup)

        # Setting page and maxpage to 1 if random mode chosen
        if self.req_args.get("s") == SortBy.RANDOM:
            page = 1
            max_page = 1
        else:
            paginator_el = soup.find("p", {"class": "pagination"})
            str_list = paginator_el.text.strip().replace("\t", " ").split(" ")
            page = int(str_list[1])
            max_page = int(str_list[3])
        return ZeroChanPage(
            category=category,
            images=imgs,
            page=page,
            max_page=max_page
        )
