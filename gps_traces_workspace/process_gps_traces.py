
from pathlib import Path
from typing import List

import geopandas as gpd  # type: ignore
from shapely.geometry import LineString  # type: ignore

from .cartesian_transforms import GeodeticToLocalCartesian
from .gpx_parser import GPXFile


def to_geopandas(gpx_files: List[GPXFile]):
    """
    Convert multiple GPXFile objects to a single GeoPandas GeoDataFrame.

    Args:
        gpx_files: A list of GPXFile objects containing GPS tracks

    Returns:
        A GeoDataFrame with points and associated attributes from all input files
    """
    # Lists to store data
    geometries = []
    timestamps = []
    track_names = []
    segment_indices = []
    file_indices = []  # New list to keep track of which file the data came from

    # Extract data from all GPXFile objects
    for file_idx, gpx_file in enumerate(gpx_files):
        for track_idx, track in enumerate(gpx_file.tracks):
            track_name = track.name

            for segment_idx, segment in enumerate(track.segments):
                local_cartesian_transformer = GeodeticToLocalCartesian()

                geometries.append(
                    LineString(
                        [
                            [point.lon, point.lat]
                            for point in segment.points
                            if len(segment.points) >= 2
                        ]
                    )
                )

                timestamps.append([point.timestamp for point in segment.points])
                track_names.append(track_name)
                segment_indices.append(segment_idx)
                file_indices.append(file_idx)  # Add file index

    # Create DataFrame
    data = {
        "geometry": geometries,
        "timestamp": timestamps,
        "track_name": track_names,
        "segment_index": segment_indices,
        "file_index": file_indices,  # Add file index to the dataframe
    }

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

    # Add metadata as attributes to the GeoDataFrame
    # We'll create a list of metadata dictionaries
    all_metadata = []
    for idx, gpx_file in enumerate(gpx_files):
        file_metadata = gpx_file.metadata.copy()
        file_metadata["file_index"] = idx
        all_metadata.append(file_metadata)

    gdf.attrs["source_files_metadata"] = all_metadata

    return gdf


def load_gpx_files_from_directory(input_directory: Path) -> List[GPXFile]:
    return [
        GPXFile.from_file(filename=file)
        for file in Path(input_directory).iterdir()
        if file.is_file() and file.suffix == ".gpx"
    ]


def main():
    dir_path = "/home/mach3/gps-traces-workspace/test_data/test_data_1"
    traces = load_gpx_files_from_directory(input_directory=dir_path)

    # traces_df = to_geopandas(traces)
    # traces_df = traces_df.dropna(subset=traces_df.columns)
    # traces_df.plot("file_index")
    # plt.show()
