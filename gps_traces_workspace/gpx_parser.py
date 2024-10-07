from datetime import datetime, timedelta
import re
from typing import List, Optional
import xml.etree.ElementTree as ET
from pathlib import Path
from attrs import define, field


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
        threshold_duration = 6000
        segment = cls()
        segment_points = [
            Trackpoint.from_xml(trkpt, namespace)
            for trkpt in element.findall("gpx:trkpt", namespace)
        ]

        if segment_points:
            start_time = segment_points[0].timestamp
            end_time = segment_points[-1].timestamp

            if start_time and end_time:
                segment_duration = end_time - start_time
                if (
                    segment_duration is not None
                    and segment_duration >= threshold_duration
                ):
                    segment.points = segment_points
                    segment.segment_duration = segment_duration

        return segment


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
            if segment.points:
                track.segments.append(TrackSegment.from_xml(trkseg, namespace))

        return track


@define
class GPXFile:
    tracks: List[Track] = field(factory=list)
    metadata: dict = field(factory=dict)

    def extract_namespace(tag: str):
        match = re.match(r"\{(.*)\}", tag)
        if match:
            return {"gpx": match.group(1)}
        return ""

    @classmethod
    def from_file(cls, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        namespace = cls.extract_namespace(root.tag)
        gpx = cls()

        metadata = root.find("gpx:metadata", namespace)
        if metadata is not None:
            for child in metadata:
                gpx.metadata[child.tag] = child.text

        # Parse tracks
        for trk in root.findall("gpx:trk", namespace):
            gpx.tracks.append(Track.from_xml(trk, namespace))

        return gpx

    @staticmethod
    def save_to_file(raw_data, filename, output_directory, concatenate_response):
        if not Path(output_directory).exists():
            Path(output_directory).mkdir()

        output_path = Path(output_directory).joinpath(filename)
        output_tree = ET.ElementTree()

        if concatenate_response:
            element = ET.fromstring(raw_data)

            tree = ET.ElementTree(element=ET.fromstring(raw_data))

        with open(output_path, "w") as file:
            tree = ET.ElementTree(element=ET.fromstring(raw_data))
            tree.write(file_or_filename=file, encoding="unicode", xml_declaration=True)
