from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import List, Optional
import xml.etree.ElementTree as ET

from attrs import define, field

from .score_based_filtering import calculate_score
from .utils import BoundingBox


@define
class Trackpoint:
    lat: float
    lon: float
    ele: Optional[float] = None
    timestamp: Optional[datetime] = None

    @classmethod
    def from_xml(cls, element, namespace):
        return cls(
            lat=float(element.get("lat")),
            lon=float(element.get("lon")),
            ele=float(element.find("ele", namespace))
            if element.find("ele", namespace) is not None
            else None,
            timestamp=int(
                datetime.fromisoformat(
                    element.find("gpx:time", namespace).text.replace("Z", "+00:00")
                ).timestamp()
            )
            if element.find("gpx:time", namespace) is not None
            else None,
        )


@define
class TrackSegment:
    points: List[Trackpoint] = field(factory=list)
    segment_duration: Optional[timedelta] = None

    @classmethod
    def from_xml(cls, element, namespace):
        segment = cls()
        segment_points = [
            Trackpoint.from_xml(trkpt, namespace)
            for trkpt in element.findall("gpx:trkpt", namespace)
        ]

        start_time = segment_points[0].timestamp
        end_time = segment_points[-1].timestamp

        if segment_points and start_time and end_time:
            segment_duration = end_time - start_time
            score = calculate_score(
                segment_duration=segment_duration, segment_points=len(segment_points)
            )

            if score >= 0.80:
                segment.points = segment_points
                segment.segment_duration = segment_duration
                return segment

        return None


@define
class Track:
    name: Optional[str] = None
    segments: List[TrackSegment] = field(factory=list)

    @classmethod
    def from_xml(cls, element, namespace):
        track = cls()
        track.name = (
            element.find("gpx:name", namespace).text
            if element.find("gpx:name", namespace) is not None
            else None
        )
        for trkseg in element.findall("gpx:trkseg", namespace):
            segment = TrackSegment.from_xml(trkseg, namespace)
            if segment is not None:
                track.segments.append(segment)

        return track


@define
class GPXFile:
    tracks: List[Track] = field(init=False, factory=list)
    metadata: dict = field(init=False, factory=dict)
    bounding_box: BoundingBox = field(
        init=False, factory=lambda: BoundingBox(0.0, 0.0, 0.0, 0.0)
    )

    def extract_namespace(tag: str):
        match = re.match(r"\{(.*)\}", tag)
        if match:
            return {"gpx": match.group(1)}
        return ""

    def get_bounding_box(element):
        left = element.get("left")
        bottom = element.get("bottom")
        right = element.get("right")
        top = element.get("top")

        return BoundingBox(
            left=float(left), bottom=float(bottom), right=float(right), top=float(top)
        )

    @classmethod
    def from_file(cls, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        namespace = cls.extract_namespace(root.tag)
        bounding_box = cls.get_bounding_box(root.attrib)
        gpx = cls()
        gpx.bounding_box = bounding_box
        metadata = root.find("gpx:metadata", namespace)
        if metadata is not None:
            for child in metadata:
                gpx.metadata[child.tag] = child.text
        # Parse tracks
        for trk in root.findall("gpx:trk", namespace):
            gpx.tracks.append(Track.from_xml(trk, namespace))

        return gpx

    @staticmethod
    def save_to_file(raw_data, bounding_box, filename, output_directory):
        if not Path(output_directory).exists():
            Path(output_directory).mkdir()

        output_path = Path(output_directory).joinpath(filename)

        with open(output_path, "w") as file:
            tree = ET.ElementTree(element=ET.fromstring(raw_data))
            root_attributes = tree.getroot().attrib
            bounding_box_info = {
                "bottom": str(bounding_box.bottom),
                "left": str(bounding_box.left),
                "top": str(bounding_box.top),
                "right": str(bounding_box.right),
            }
            root_attributes.update(bounding_box_info)
            tree.write(file_or_filename=file, encoding="unicode", xml_declaration=True)
            print(f"Traces are saved to: {filename}.")
