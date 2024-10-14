import argparse
from pathlib import Path

import requests

from .gpx_parser import GPXFile
from .utils import BoundingBox


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
    parser.add_argument(
        "--concatenate",
        type=bool,
        help="Combines the request response into a single file till the size_limit is reached.  ",
    )
    parser.add_argument(
        "--output-dir", type=Path, help="output directory for gpx files"
    )

    args = parser.parse_args()

    if not all([args.left, args.bottom, args.right, args.top, args.output_dir]):
        parser.error("Please provide all BoundingBox coordinates")

    return args


def download_gps_traces(
    bounding_box: BoundingBox,
    output_dir: Path,
    concatenate_response: bool,
    max_pages: int = 10,
    max_failure_count: int = 3,
):
    url = "https://api.openstreetmap.org/api/0.6/trackpoints?bbox={left},{bottom},{right},{top}&page={page_number}"
    current_failure_count = 0
    page_number = 1

    while True:
        try:
            if page_number > max_pages:
                print(f"Reached the page limit: {page_number}")
                break

            response = requests.get(
                url=url.format(
                    left=bounding_box.left,
                    bottom=bounding_box.bottom,
                    right=bounding_box.right,
                    top=bounding_box.top,
                    page_number=page_number,
                )
            )

            if response.status_code == 200:
                GPXFile.save_to_file(
                    raw_data=response.content,
                    bounding_box=bounding_box,
                    filename=f"test_gpx_updated_{page_number}.gpx",
                    output_directory=output_dir,
                )
                page_number += 1
            else:
                current_failure_count += 1
                print(
                    f"Error on page {page_number}: Status code {response.status_code}"
                )

                if current_failure_count >= max_failure_count:
                    print(
                        f"Stopping due to {current_failure_count} consecutive errors."
                    )
                    break

        except requests.exceptions.RequestException as e:
            current_failure_count += 1
            print(
                f"Failed to fetch page {page_number}, Status code: {response.status_code} and Error: {e}"
            )

            if current_failure_count >= max_failure_count:
                print(f"Stopping due to {current_failure_count} consecutive errors.")
                break


def main():
    args = parse_arguments()

    download_gps_traces(
        bounding_box=BoundingBox(
            left=args.left, bottom=args.bottom, right=args.right, top=args.top
        ),
        output_dir=args.output_dir,
        concatenate_response=True,
    )
