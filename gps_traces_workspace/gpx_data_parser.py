import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import XMLParser, Element
from attr import define, field
from typing import List


@define
class GpxParser:
    raw_data: str = field()
    data: Element = field()
    element_tree: ElementTree = field(default=ElementTree())
    track_segments: List
    track_count: int

    def parse_raw_data(self):
        self.element = ElementTree.fromstring(
            self.raw_data, parser=XMLParser(encoding="utf-8")
        )

    # def get_tracks_from_data(self):
    #     root = self.data.

    @data.validator
    def check_xml_content(self, attribute, value):
        root = value.getroot()
        if root.find("tag") is None:
            raise ValueError(f"Missing required GPX tag, check the response data.")
