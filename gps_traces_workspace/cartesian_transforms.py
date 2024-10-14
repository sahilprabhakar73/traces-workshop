from typing import Tuple

from attrs import define, field
import numpy as np
from pyproj import Transformer


@define
class GeodeticToLocalCartesian:
    geodetic_reference = field(init=True, factory=Tuple)
    enu_reference = field(init=False, factory=Tuple)
    ecef_transformer = field(init=False)

    def __attrs_post_init__(self):
        self.ecef_transformer = Transformer.from_crs(
            "EPSG:4326", "EPSG:4978", always_xy=True
        )

        self.enu_reference = self.ecef_transformer.transform(
            self.geodetic_reference[0],
            self.geodetic_reference[1],
            self.geodetic_reference[2],
        )

    def ecef_to_enu(self, geodetic_coordinate):
        x_coord, y_coord, z_coord = self.ecef_transformer(
            geodetic_coordinate[0], geodetic_coordinate[1], geodetic_coordinate[2]
        )

        x_diff = x_coord - self.enu_reference[0]
        y_diff = y_coord - self.enu_reference[1]
        z_diff = z_coord - self.enu_reference[2]

        # Convert reference latitude and longitude to radians
        lat_rad = np.deg2rad(self.geodetic_reference[0])
        lon_rad = np.deg2rad(self.geodetic_reference[1])

        # Compute the transformation matrix from ECEF to ENU
        t = np.array(
            [
                [-np.sin(lon_rad), np.cos(lon_rad), 0],
                [
                    -np.sin(lat_rad) * np.cos(lon_rad),
                    -np.sin(lat_rad) * np.sin(lon_rad),
                    np.cos(lat_rad),
                ],
                [
                    np.cos(lat_rad) * np.cos(lon_rad),
                    np.cos(lat_rad) * np.sin(lon_rad),
                    np.sin(lat_rad),
                ],
            ]
        )

        # Apply the transformation matrix to the ECEF coordinate differences
        enu = t @ np.array([x_diff, y_diff, z_diff])
        return enu[0], enu[1], enu[2]  # Returns (East, North, Up)
