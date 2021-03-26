from typing import List

import requests
from bs4 import BeautifulSoup
import json

from dtypes import (
    PictureSize, ZeroChanCategory,
    ZeroChanImage, ZeroChanPage, SortBy
)
from exceptions import NoPicturesFound


class ZeroChan:
    WEBSITE_URL = "https://www.zerochan.net"

    # TODO: filter by image size by pixel, alt and other

    def __init__(self):
        self._tag = ""
        self._page = 1
        self._sort_by = SortBy.LAST
        self._size = PictureSize.ALL_SIZES
        self.cookies = dict(
            z_lang="en"
        )
        self.req_args = {}

    def size(self, size: PictureSize) -> 'ZeroChan':
        self._size = size
        return self

    def sort(self, sort_by: SortBy) -> 'ZeroChan':
        self._sort_by = sort_by
        return self

    def page(self, page_num: int) -> 'ZeroChan':
        self._page = page_num
        return self

    def tag(self, title: str) -> 'ZeroChan':
        self._tag = title
        return self

    def authorize(self, z_hash: str, z_id: str):
        self.cookies.update(dict(
            z_hash=z_hash,
            z_id=z_id
        ))
        return self

    def _get_soup(self):
        self.req_args.update(dict(
            p=self._page,
            s=self._sort_by,
            d=int(self._size)
        ))
        req = requests.get(
            f"{self.WEBSITE_URL}/{self._tag}",
            params=self.req_args,
            cookies=self.cookies
        )
        #print(req.url)
        return BeautifulSoup(req.content, "html.parser")

    def category(self) -> ZeroChanCategory:
        soup = self._get_soup()
        content_el = soup.find("script", {"type": "application/ld+json"})
        if content_el is None:
            raise NoPicturesFound
        page_data = json.loads("".join(content_el.contents))
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
            if getattr(pic.a, "img") is None:
                # parser try to parse "Members only" link if not authorized
                # idk why it's going do
                continue
            title = pic.a.img.get("title")
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

    def pics(self) -> ZeroChanPage:
        soup = self._get_soup()
        pics_soup = soup.find("ul", dict(id="thumbs2"))

        if pics_soup is None:
            raise NoPicturesFound
        imgs = self._parse_pics(pics_soup)

        # Setting page and maxpage to 1 if random mode chosen
        if self._sort_by == SortBy.RANDOM:
            page = 1
            max_page = 1
        else:
            paginator_el = soup.find("p", {"class": "pagination"})
            str_list = paginator_el.text.strip().replace("\t", " ").split(" ")
            if self._page == 1:
                page = int(str_list[1])
                max_page = int(str_list[3])
            else:
                page = int(str_list[4])
                max_page = int(str_list[6])
        return ZeroChanPage(
            images=imgs,
            page=page,
            max_page=max_page
        )
