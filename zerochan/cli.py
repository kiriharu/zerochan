from dtypes import SortBy, PictureSize
from lib import ZeroChan
from c_exceptions import NoPicturesFound
import argparse
import datetime
import os
import requests

PICS_DIR = os.path.join(os.getcwd(), "zerochan_pics")

pic_sizes = {
    1: PictureSize.ALL_SIZES,
    2: PictureSize.BIGGER_AND_BETTER,
    3: PictureSize.BIG_AND_HUGE
}

sorted_by = {
    1: SortBy.LAST,
    2: SortBy.POPULAR,
    3: SortBy.RANDOM
}


def super_duper_logger(text: str, level: str):
    """This is my secret development, shh!"""
    print(f"[{datetime.datetime.now()}] [{level}]: {text}")


def create_parser():
    # TODO: change prog
    parser = argparse.ArgumentParser(
        epilog="March 2021"
    )

    parser.add_argument(
        "--title",
        help="Title name to parse",
        required=True
    )
    parser.add_argument(
        "-s",
        "--size",
        default=1,
        type=int,
        choices=[1, 2, 3],
        help="Image size: 1 - All (default), 2 - bigger and better, 3 - large only"
    )
    parser.add_argument(
        "-m",
        "--mode",
        default=1,
        type=int,
        choices=[1, 2, 3],
        help="Sort mode: 1 - Last (default), 2 - Popular, 3 - Random"
    )
    parser.add_argument(
        "-p",
        "--page",
        default=1,
        type=int,
        help="Start page to download"
    ),
    parser.add_argument(
        "-a",
        "--authorize",
        metavar="z_hash;z_id",
        help="z_hash and z_id from cookies like z_hash;z_id"
    )
    parser.add_argument(
        "-c",
        "--check_mode",
        action="store_true",
        help="Only check mode, don't download pics, just print urls."
    )
    parser.add_argument(
        "-o",
        "--onlypage",
        help="Download only selected page",
        action="store_true"
    )
    return parser


def download_file(url: str, path: str):
    filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(path, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=2048):
                f.write(chunk)
    super_duper_logger(
        f"Downloaded {filename} to {path}", "DOWNLOADER"
    )


def get_pics(zerochan_instance: ZeroChan):
    try:
        return zerochan_instance.pics()
    except NoPicturesFound:
        super_duper_logger("No pictures found on page.", "ERROR")


if __name__ == "__main__":
    parser_instance = create_parser()
    args = parser_instance.parse_args()

    zerochan = ZeroChan()\
        .search(args.title)\
        .size(pic_sizes.get(args.size))\
        .sort(sorted_by.get(args.mode))\
        .page(args.page)

    if args.authorize:
        z_hash, z_id = args.authorize.split(";")
        zerochan.authorize(z_hash, z_id)

    data = get_pics(zerochan)

    page = data.page
    if args.onlypage:
        max_page = page
    else:
        max_page = data.max_page

    if not args.check_mode:
        call_dir = os.getcwd()
        try:
            os.mkdir(PICS_DIR)
        except FileExistsError:
            pass

    for i in range(page, max_page):
        super_duper_logger(f"Get page {i}/{max_page}", "REQUEST")
        data_page = get_pics(zerochan.page(i))
        if data_page is None:
            continue
        for image in data_page.images:
            super_duper_logger(
                f"Getting image {image.title}: {image.url} with size {image.size} {image.kbsize}",
                "PARSER"
            )
            if not args.check_mode:
                download_file(image.url, PICS_DIR)
