# hospital_police_finder_enhanced.py
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import time
from typing import Tuple, List, Dict

# Optional: folium + streamlit_folium for interactive map
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

st.set_page_config(page_title="Nearby Resources Finder (India) — Enhanced", layout="wide")
st.title("Nearby Resources Finder — India")

# --- Sidebar controls ---
st.sidebar.header("Search Options")

place_name = st.sidebar.text_input("Enter location (city/area/sub-area):", value="")
use_coords = st.sidebar.checkbox("Enter coordinates manually instead", value=False)
if use_coords:
    lat_input = st.sidebar.number_input("Latitude", format="%.6f")
    lon_input = st.sidebar.number_input("Longitude", format="%.6f")
else:
    lat_input = lon_input = None

radius_km = st.sidebar.slider("Search radius (km)", min_value=1, max_value=50, value=10, step=1)
units = st.sidebar.selectbox("Distance units", ["km", "miles"])
max_results_per_type = st.sidebar.number_input("Max results per type", min_value=10, max_value=500, value=100, step=10)

st.sidebar.markdown("---")
# POI choices (user can multi-select)
available_pois = {
    "Hospital": "[amenity=hospital]",
    "Clinic": "[healthcare=clinic]",
    "Medical Camp": "[healthcare=clinic][charity=yes]",
    "Pharmacy": "[amenity=pharmacy]",
    "Doctors": "[healthcare=doctors]",
    "Police Station": "[amenity=police]",
    "Ambulance Station": "[emergency=ambulance]",
    "Blood Bank": "[amenity=blood_donation]",
    "Ambulance Service (tagged)": "[service=ambulance]",
    "Community Health Centre": "[healthcare=health_centre]"
}
selected_pois = st.sidebar.multiselect("Select resource types to search", list(available_pois.keys()),
                                       default=["Hospital", "Police Station", "Pharmacy"])

st.sidebar.markdown("---")
show_map_type = st.sidebar.selectbox("Map type", ["Streamlit simple map (fast)", "Folium map (interactive)"] if FOLIUM_AVAILABLE else ["Streamlit simple map (fast)"])
nearest_n = st.sidebar.number_input("Show nearest N results overall (0 = show all)", min_value=0, max_value=500, value=0, step=1)

st.sidebar.markdown("---")
st.sidebar.info("Respect Nominatim & Overpass usage policies. Do not automate heavy queries.")

# Emergency contacts (India) — shown on sidebar for quick reference
st.sidebar.markdown("### Emergency numbers (India)")
st.sidebar.write("Police: 100")
st.sidebar.write("Ambulance: 102 / 108 (varies by state)")
st.sidebar.write("Fire: 101")

# --- Overpass endpoint & functions ---
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def km_to_miles(km: float) -> float:
    return km * 0.621371

# Caching geocode results and query results to reduce repeated requests
@st.cache_data(ttl=60*60*24)  # cache for 1 day
def geocode_location(query: str) -> Tuple[float, float]:
    geolocator = Nominatim(user_agent="hospital_police_finder_enhanced")
    loc = geolocator.geocode(query, timeout=10)
    if not loc:
        raise ValueError("Location not found")
    return loc.latitude, loc.longitude

@st.cache_data(ttl=60*60)  # cache Overpass results for 1 hour based on query string
def overpass_query(query: str) -> Dict:
    res = requests.get(OVERPASS_URL, params={'data': query}, timeout=60)
    if res.status_code != 200:
        raise ConnectionError(f"Overpass returned HTTP {res.status_code}")
    return res.json()

def build_overpass_query(lat: float, lon: float, radius_m: int, tag: str, max_res: int) -> str:
    q = f"""
    [out:json][timeout:25];
    (
      node(around:{radius_m},{lat},{lon}){tag};
      way(around:{radius_m},{lat},{lon}){tag};
      relation(around:{radius_m},{lat},{lon}){tag};
    );
    out center {max_res};
    """
    return q

def extract_lat_lon(element: dict):
    if 'lat' in element and 'lon' in element:
        return element.get('lat'), element.get('lon')
    center = element.get('center')
    if center and 'lat' in center and 'lon' in center:
        return center['lat'], center['lon']
    return None, None

def fetch_resources(lat: float, lon: float, radius_km: float, selected: List[str], max_per_type: int) -> List[dict]:
    results = []
    radius_m = int(radius_km * 1000)
    headers = {"Accept": "application/json"}
    for poi_name in selected:
        tag = available_pois.get(poi_name)
        if not tag:
            continue
        q = build_overpass_query(lat, lon, radius_m, tag, max_per_type)
        try:
            data = overpass_query(q)
            elements = data.get('elements', [])
            for el in elements:
                tags = el.get('tags', {})
                name = tags.get('name', 'Unknown')
                rlat, rlon = extract_lat_lon(el)
                if rlat is None or rlon is None:
                    continue
                # compute distance in km
                dist_km = geodesic((lat, lon), (rlat, rlon)).km
                area = tags.get('addr:full') or tags.get('addr:street') or tags.get('addr:suburb') \
                       or tags.get('addr:city') or tags.get('addr:state') or f"Lat:{rlat}, Lon:{rlon}"
                results.append({
                    "Name": name,
                    "Type": poi_name,
                    "Distance_km": round(dist_km, 3),
                    "Latitude": rlat,
                    "Longitude": rlon,
                    "Location": area,
                    "Tags": tags
                })
            # polite pause
            time.sleep(0.8)
        except Exception as e:
            st.warning(f"Failed to fetch {poi_name}: {e}")
    return results

# --- Main action ---
find_button = st.button("Find Nearby Resources")

if find_button:
    if use_coords:
        if lat_input is None or lon_input is None:
            st.error("Enter both latitude and longitude.")
            st.stop()
        user_lat, user_lon = lat_input, lon_input
    else:
        if not place_name or not place_name.strip():
            st.error("Please enter a location.")
            st.stop()
        try:
            with st.spinner("Geocoding..."):
                user_lat, user_lon = geocode_location(place_name)
        except Exception as e:
            st.error(f"Geocoding failed: {e}")
            st.stop()

    st.success(f"Using coordinates: {user_lat:.6f}, {user_lon:.6f}")
    with st.spinner("Querying Overpass and gathering resources..."):
        raw_results = fetch_resources(user_lat, user_lon, radius_km, selected_pois, int(max_results_per_type))

    if not raw_results:
        st.info("No resources found within the specified radius.")
    else:
        df = pd.DataFrame(raw_results)
        # deduplicate by name + lat + lon
        df = df.drop_duplicates(subset=["Name", "Latitude", "Longitude"])

        # sort by distance and optionally show nearest N
        df = df.sort_values("Distance_km").reset_index(drop=True)
        if nearest_n and nearest_n > 0:
            df = df.head(int(nearest_n))

        # convert units if needed
        if units == "miles":
            df["Distance"] = df["Distance_km"].apply(lambda x: round(km_to_miles(x), 3))
            dist_col_name = "Distance (miles)"
        else:
            df["Distance"] = df["Distance_km"].apply(lambda x: round(x, 3))
            dist_col_name = "Distance (km)"

        display_df = df[["Name", "Type", "Distance", "Location", "Latitude", "Longitude"]].rename(columns={"Distance": dist_col_name})
        st.subheader(f"Found {len(display_df)} resources within {radius_km} km")
        st.dataframe(display_df)

        # CSV export
        csv = display_df.to_csv(index=False)
        st.download_button("Download results as CSV", data=csv, file_name="nearby_resources.csv", mime="text/csv")

        # Show map
        if show_map_type.startswith("Folium") and FOLIUM_AVAILABLE:
            st.markdown("**Interactive map (Folium)**")
            # build folium map centered on user location
            m = folium.Map(location=[user_lat, user_lon], zoom_start=13)
            # add a marker for user
            folium.Marker([user_lat, user_lon], popup="You are here", icon=folium.Icon(color="blue", icon="user")).add_to(m)

            # cluster markers
            from folium.plugins import MarkerCluster
            marker_cluster = MarkerCluster().add_to(m)
            for _, row in df.iterrows():
                popup_html = f"<b>{row['Name']}</b><br/>{row['Type']}<br/>{round(row['Distance_km'],2)} km<br/>{row['Location']}<br/>" \
                             f"<a target='_blank' href='https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}'>Open in Google Maps</a>"
                folium.Marker([row['Latitude'], row['Longitude']], popup=popup_html).add_to(marker_cluster)
            # display
            st_folium(m, width=900, height=600)
        else:
            # fallback simple map
            st.markdown("**Map preview**")
            try:
                map_df = df[["Latitude", "Longitude", "Name"]].rename(columns={"Latitude": "lat", "Longitude": "lon"})
                st.map(map_df)
            except Exception:
                st.info("Map preview unavailable in this environment. Try the Folium option if available.")

        # Show quick stats / missing categories
        types_present = set(df["Type"].unique())
        for poi in selected_pois:
            if poi not in types_present:
                st.info(f"No {poi} found near your location.")

        st.success("Search completed.")
