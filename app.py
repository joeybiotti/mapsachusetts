import json

import duckdb
import geopandas as gpd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title='Mapsachusetts Trails', page_icon='🌲', layout='wide')


@st.cache_data
def load_trail_data():
    """Reads processed GeoParquet via DuckDB, transforms EPSG, flips axis order, and loads GeoDataFrame."""
    conn = duckdb.connect()
    conn.execute('INSTALL spatial; LOAD spatial;')

    # ST_FlipCoordinates swaps (Lat, Lon) to standard GIS (Lon, Lat)
    query = """
        SELECT 
            name,
            surface,
            length_meters,
            length_miles,
            ST_AsText(
                ST_FlipCoordinates(
                    ST_Transform(geometry, 'EPSG:26986', 'EPSG:4326')
                )
            ) AS wkt_geometry
        FROM 'data/processed/trails.parquet'
    """
    df = conn.execute(query).df()
    conn.close()

    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['wkt_geometry']), crs='EPSG:4326')

    return gdf


gdf = load_trail_data()

st.write('CRS:', gdf.crs)
st.write('First Geometry WKT:', gdf.geometry.iloc[0].wkt if not gdf.empty else 'Empty')
st.write('Centroid (Lon, Lat):', gdf.geometry.union_all().centroid.x, gdf.geometry.union_all().centroid.y)

# Header
st.title('Mapsachusetts Trails Explorer')
st.markdown('Exploring Mass Trails and rail trails powered by DuckDB.')

# Sidebar
st.sidebar.header('Trail Filters')
surfaces = ['All'] + sorted(gdf['surface'].dropna().unique().tolist())
selected_surface = st.sidebar.selectbox('Filter by Surface Type', surfaces)

if selected_surface != 'All':
    filtered_gdf = gdf[gdf['surface'] == selected_surface].copy()
else:
    filtered_gdf = gdf.copy()

st.sidebar.markdown('---')
st.sidebar.metric('Total Trail Segments', len(filtered_gdf))
st.sidebar.metric('Total Miles', round(filtered_gdf['length_miles'].sum(), 2))

# Map Section
st.subheader('Trail Map')

if not filtered_gdf.empty:
    # 1. Calculate map center point
    centroid = filtered_gdf.geometry.union_all().centroid
    center_lat = float(centroid.y)
    center_lon = float(centroid.x)

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=0,
    )

    # 2. Convert GeoDataFrame explicitly to GeoJSON dict for PyDeck
    geojson_data = json.loads(filtered_gdf.to_json())

    # 3. Define Path / GeoJson layer
    path_layer = pdk.Layer(
        'GeoJsonLayer',
        data=geojson_data,
        opacity=0.8,
        stroked=True,
        filled=False,
        get_line_color=[16, 185, 129],
        get_line_width=25,
        get_line_width_min_pixels=3,
        pickable=True,
    )

    r = pdk.Deck(
        layers=[path_layer],
        initial_view_state=view_state,
        tooltip={
            'html': '<b>Trail:</b> {name}<br/><b>Surface:</b> {surface}<br/><b>Distance:</b> {length_miles} mi',
            'style': {'color': 'white'},
        },
    )

    st.pydeck_chart(r)
else:
    st.warning('No trail segments found for the selected filter.')

# Data Table
with st.expander('View Raw Segment Data'):
    st.dataframe(
        filtered_gdf[['name', 'surface', 'length_miles', 'length_meters']],
        width='stretch',
    )
