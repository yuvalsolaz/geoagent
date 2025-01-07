import os
from typing import Any, Dict, Type, List
import json
import shapely
from shapely.ops import unary_union
from shapely.geometry import shape, MultiPolygon, mapping
from shapely.geometry.polygon import Polygon
import re
from config import SIMPLIFY_SHAPE_TOLERANCE


class GeoDatabase:
    def __init__(self, data_dir):
        self.global_geometries: Dict[str, Any] = {}
        self._load(data_dir)

    def _normalize_key(self, location: str) -> str:
        if '|type:' in location:
            location = location.split('|type:', 1)[0].strip()
        normalized = re.sub(r'[^a-zA-Z0-9]', '_', location.lower())
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip('_')

    # Load all geojson files in data_dir
    def _load(self, data_dir):
        for file in os.listdir(data_dir):
            if file.endswith(".geojson"):
                self._load_geojson(os.path.join(data_dir, file))

    # Load geojson file
    def _load_geojson(self, geojson_file: str):
        try:
            with open(geojson_file, 'r') as f:
                geojson_data = json.load(f)
                for feature in geojson_data["features"]:
                    name = feature['properties'].get('NAME_EN', '').lower()
                    multiline = shape(feature['geometry']).boundary
                    print(f'adding {name} to geo_database')
                    self.set_geometries(location=name, geometries=multiline)

        except Exception as ex:
            print(f"Error loading borderlines file: {str(ex)}")

    def get_geometry(self, location):
        return self.global_geometries.get(location.lower(), None) if location else None

    def set_geometries(self, location: str, geometries: Any) -> None:
        normalized_key = self._normalize_key(location)
        self.global_geometries[normalized_key] = geometries

    def get_geometries(self) -> Dict[str, Any]:
        return self.global_geometries.copy()

    def get_location_keys(self) -> List[str]:
        return list(self.global_geometries.keys())
