import duckdb
import geopandas as gpd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title='Mapsachusetts Rail Trails', page_icon='*', layout='wide')


@st.cache_data
def load_trail_data():
    """Reads processed GeoParquet via DuckDB and converts to GeoDataFrame."""
    conn = duckdb.connect()
    conn.execute('INSTALL spatial; LOAD spatial;')

    query = """
        SELECT 
            trail_name,
            surface_type,
            smoothness,
            length_meters,
            ROUND(length_meters / 1609.34, 2) AS length_miles,
            ST_AsText(geom) AS wkt_geom
        FROM 'data/processed/rail_trails.parquet'
    """
    df = conn.execute(query).df()
    conn.close()

    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['wkt_geom']), crs='EPSG:4326')

    return gdf


gdf = load_trail_data()

# Header
st.title('Mapsachusetts Rail Trails Explorer')
st.markdown('Exploring Mass Rail Trails and rail trails powered by DuckDB.')

# Sidebar
st.sidebar.header('Trail Filters')
surfaces = ['All'] + sorted(gdf['surface_type'].unique().tolist())
selected_surface = st.sidebar.selectbox('Filter by Surface Type', surfaces)

if selected_surface != 'All':
    filtered_gdf = gdf[gdf['surface_type'] == selected_surface]
else:
    filtered_gdf = gdf

st.sidebar.markdown('---')
st.sidebar.metric('Total Trail Segments', len(filtered_gdf))
st.sidebar.metric('Total Miles', round(filtered_gdf['length_miles'].sum(), 2))

# Map
st.subheader('Trail Map')
centroid = filtered_gdf.geometry.unary_union.centroid
view_state = pdk.ViewState(
    latitude=centroid.y,
    longitude=centroid.x,
    zoom=11,
    pitch=0,
)

path_layer = pdk.Layer(
    'GeoJsonLayer',
    filtered_gdf,
    opacity=0.8,
    stroked=True,
    filled=False,
    get_line_color=[16, 185, 129],
    get_line_width=25,
    pickable=True,
)

r = pdk.Deck(
    layers=[path_layer],
    initial_view_state=view_state,
    tooltip={
        'html': '<b>Trail:</b> {trail_name}<br/><b>Surface:</b> {surface_type}<br/><b>Distance:</b> {length_miles} mi',
        'style': {'color': 'white'},
    },
)

st.pydeck_chart(r)

# Data Table
with st.expander('View Raw Segment Data'):
    st.dataframe(
        filtered_gdf[
            [
                'trail_name',
                'surface_type',
                'smoothness',
                'length_miles',
                'length_meters',
            ]
        ],
        use_container_width=True,
    )
