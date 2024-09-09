import argparse
from typing import NamedTuple
import xml.etree.ElementTree as ElementTree
import requests


class BoundingBox(NamedTuple):
    left: float
    bottom: float
    right: float
    top: float


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Add BoundingBox coordinates via command line arguments"
    )
    parser.add_argument("--left", type=float, help="Left coordinate of the BoundingBox")
    parser.add_argument(
        "--bottom", type=float, help="Bottom coordinate of the BoundingBox"
    )
    parser.add_argument(
        "--right", type=float, help="Right coordinate of the BoundingBox"
    )
    parser.add_argument("--top", type=float, help="Top coordinate of the BoundingBox")

    args = parser.parse_args()

    if not all([args.left, args.bottom, args.right, args.top]):
        parser.error("Please provide all BoundingBox coordinates")

    return BoundingBox(
        left=args.left, bottom=args.bottom, right=args.right, top=args.top
    )


def request_to_download_gps_traces(bounding_box: BoundingBox):
    url = "https://api.openstreetmap.org/api/0.6/trackpoints?bbox={left},{bottom},{right},{top}&page={page_number}"
    response = requests.get(
        url=url.format(
            left=bounding_box.left,
            bottom=bounding_box.bottom,
            right=bounding_box.right,
            top=bounding_box.top,
            page_number=0,
        )
    )
    if response.status_code == 200:
        data = response.content
        print(data)
    else:
        print(f"Failed to retrieve data: {response.status_code}")


def parse_gpx_file(data):
    root = ElementTree.fromstring(data)
    


def main():
    bounding_box = parse_arguments()
    request_to_download_gps_traces(bounding_box=bounding_box)
