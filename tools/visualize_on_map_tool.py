import folium
from folium import plugins
import geopandas as gpd
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from utils.geo_state_manager import GeoStateManager

geo_state = GeoStateManager()

basemaps = {
    'Google Maps': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps',
        overlay=True,
        control=True
    ),
    # 'Google Satellite': folium.TileLayer(
    #     tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    #     attr='Google',
    #     name='Google Satellite',
    #     overlay=True,
    #     control=True
    # ),
    'Google Terrain': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Terrain',
        show=False,
        overlay=True,
        control=True
    ),
    'Google Satellite Hybrid': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        show=False,
        overlay=True,
        control=True
    )
    # 'Esri Satellite': folium.TileLayer(
    #     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    #     attr='Esri',
    #     name='Esri Satellite',
    #     overlay=True,
    #     control=True
    # )
}

def create_map():
    # Create a folium map
    bounds = geo_state.get_boundaries()
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Create a folium map object.
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, height=500)

    # Add custom basemaps
    for basemap in basemaps.values():
        basemap.add_to(m)

    # Add query locations polygons to the map:
    for key in geo_state.global_geometries:
        geom = unary_union(geo_state.global_geometries[key])
        polygon_name = key
        # Add the polygon to the map
        folium.GeoJson(
            geom,
            style_function=lambda x: {'fillColor': 'gray', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.2}
        ).add_to(m)

        # Add a marker with polygon name
        centroid = geom.centroid
        folium.Marker(
            [centroid.y, centroid.x],
            popup=f'Polygon: {polygon_name}',
            icon=folium.DivIcon(html=f'<div style="font-size: 24pt; color : blue">{polygon_name}</div>')
        ).add_to(m)

    # Add polygons and markers to the map
    class_color = {'Airport': 'green',
                   'Highway': 'yellow',
                   'Residential': 'red',
                   'Industrial': 'black',
                   'Other': 'blue'}
    gdf = geo_state.get_gdf()
    if not gdf.empty:
        for _, row in gdf.iterrows():
            geom = row['geom']
            id = row['id'].split('_')[-1]
            event_class = row["class"]
            region = row["region"]
            startdate=str(row["startdate"]).split()[0]
            enddate=str(row["enddate"]).split()[0]
            buildfromzero = row["buildfromzero"]
            confidance = row["confidence"]
            # Add the polygon to the map
            folium.GeoJson(
                data=geom,
                weight=2,
                color='black',
                fill=True,
                fill_color=class_color[event_class],
                fill_opacity=0.3
            ).add_to(m)

            # Add a marker with polygon number
            centroid = geom.centroid
            open_area = "open area" if buildfromzero else ""
            folium.Marker(
                [centroid.y, centroid.x],
                popup=f'Id: {id} \n{event_class} \n{region} ',
                tooltip=f'{event_class}: {id}  {region} from:{startdate} to:{enddate} score:{confidance} {open_area}',
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color : black;">{id}</div>')
            ).add_to(m)

    # Fit the map to the bounds of the geometries
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    # Add a layer control panel to the map.

    m.add_child(folium.LayerControl())
    return m
