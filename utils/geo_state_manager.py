from functools import wraps
import threading
from typing import Any, Dict, Type, Optional, List
from shapely.geometry import Polygon
from shapely.ops import unary_union
import geopandas as gpd

import re

def singleton(cls: Type[Any]) -> Type[Any]:
    instances: Dict[Type[Any], Any] = {}
    lock = threading.Lock()
    
    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class GeoStateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.global_geometries: Dict[str, Any] = {}
        self.gdf: Optional[gpd.GeoDataFrame] = None

    def _normalize_key(self, location: str) -> str:
        if '|type:' in location:
            location = location.split('|type:', 1)[0].strip()
        normalized = re.sub(r'[^a-zA-Z0-9א-ת]', '_', location.lower())
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip('_')

    def reset(self) -> None:
        with self._lock:
            self.global_geometries = {}
            self.gdf = None

    def set_geometries(self, location: str, geometries: Any) -> None:
        with self._lock:
            normalized_key = self._normalize_key(location)
            self.global_geometries[normalized_key] = geometries

    def get_geometries(self) -> Dict[str, Any]:
        with self._lock:
            return self.global_geometries.copy()
        
    def get_location_keys(self) -> List[str]:
        with self._lock:
            return list(self.global_geometries.keys())

    def set_gdf(self, gdf: gpd.GeoDataFrame) -> None:
        with self._lock:
            self.gdf = gdf

    def get_gdf(self) -> Optional[gpd.GeoDataFrame]:
        with self._lock:
            return self.gdf.copy() if self.gdf is not None else gpd.GeoDataFrame()

    def get_boundaries(self):
        geom = None
        for g in self.get_geometries():
            union_g = unary_union(self.global_geometries[g])
            geom = unary_union([geom, union_g]) if geom else union_g
        gdf = self.get_gdf()
        if gdf.empty:
            return geom.bounds if geom else [34.5, 32, 35, 33]

        minx = min(geom.bounds[0], gdf.geom.total_bounds[0])
        miny = min(geom.bounds[1], gdf.geom.total_bounds[1])
        maxx = max(geom.bounds[2], gdf.geom.total_bounds[2])
        maxy = max(geom.bounds[3], gdf.geom.total_bounds[3])
        return [minx, miny, maxx, maxy]


