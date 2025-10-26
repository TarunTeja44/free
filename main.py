import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# --- Streamlit Page Config ---
st.set_page_config(page_title="🚨 Emergency Services Finder", layout="wide")

# --- Title ---
st.markdown("<h1 style='text-align:center;'>🚨 Emergency Services Finder (India)</h1>", unsafe_allow_html=True)
st.write("Find nearby hospitals, clinics, police stations, pharmacies, and more — powered by OpenStreetMap and AI geolocation!")

# --- Input Section ---
st.sidebar.header("🔍 Search Options")
location_input = st.sidebar.text_input("Enter your location (City, Area, or PIN):", "Hyderabad")
radius_km = st.sidebar.slider("Search radius (km):", 1, 20, 5)
service_types = st.sidebar.multiselect(
    "Select service categories:",
    ["Hospital", "Clinic", "Doctors", "Pharmacy", "Police Station", "Fire Station", "ATM", "Embassy", "Tourist Office"],
    default=["Hospital", "Police Station", "Pharmacy"]
)

# --- Geocoding ---
@st.cache_data
def get_coordinates(place):
    try:
        geolocator = Nominatim(user_agent="emergency_locator")
        loc = geolocator.geocode(place)
        if loc:
            return loc.latitude, loc.longitude
        return None
    except:
        return None

coords = get_coordinates(location_input)

if not coords:
    st.error("❌ Could not find that location. Try entering a more specific name.")
    st.stop()

user_loc = coords

# --- Query Overpass API ---
@st.cache_data
def get_places(lat, lon, radius, services):
    results = []
    for service in services:
        query = f"""
        [out:json];
        (
          node["amenity"="{service.lower()}"](around:{radius*1000},{lat},{lon});
          way["amenity"="{service.lower()}"](around:{radius*1000},{lat},{lon});
        );
        out center;
        """
        try:
            r = requests.get("https://overpass-api.de/api/interpreter", params={'data': query})
            if r.status_code == 200:
                data = r.json()
                for el in data['elements']:
                    lat_ = el.get('lat', el.get('center', {}).get('lat'))
                    lon_ = el.get('lon', el.get('center', {}).get('lon'))
                    name = el.get('tags', {}).get('name', 'Unnamed')
                    addr = el.get('tags', {}).get('addr:full') or el.get('tags', {}).get('addr:street', 'Address not available')
                    phone = el.get('tags', {}).get('phone', 'Not available')
                    dist = round(((abs(lat - lat_)**2 + abs(lon - lon_)**2)**0.5) * 111, 2) if lat_ and lon_ else None
                    results.append({
                        "Name": name,
                        "Type": service.title(),
                        "Latitude": lat_,
                        "Longitude": lon_,
                        "Address": addr,
                        "Phone": phone,
                        "Distance_km": dist,
                        "Google_Maps": f"https://www.google.com/maps?q={lat_},{lon_}",
                        "Directions": f"https://www.google.com/maps/dir/{lat},{lon}/{lat_},{lon_}"
                    })
        except:
            pass
    return pd.DataFrame(results)

with st.spinner("🔎 Fetching nearby emergency services..."):
    df = get_places(user_loc[0], user_loc[1], radius_km, service_types)

if df.empty:
    st.warning("😕 No results found within this area and radius.")
    st.stop()

# --- Results Header ---
st.markdown('<h2 style="margin-top:20px;">🗺️ Interactive Map</h2>', unsafe_allow_html=True)

# --- Map Setup ---
colors = {
    'Hospital': 'red', 'Clinic': 'pink', 'Doctors': 'purple',
    'Pharmacy': 'green', 'Police Station': 'blue', 'Fire Station': 'orange',
    'ATM': 'darkpurple', 'Embassy': 'lightgray', 'Tourist Office': 'cadetblue'
}

icons = {
    'Hospital': 'plus-square', 'Clinic': 'stethoscope', 'Doctors': 'user-md',
    'Pharmacy': 'prescription-bottle', 'Police Station': 'shield-alt', 'Fire Station': 'fire-extinguisher',
    'ATM': 'money-bill', 'Embassy': 'university', 'Tourist Office': 'info-circle'
}

m = folium.Map(location=user_loc, zoom_start=13)
marker_cluster = MarkerCluster().add_to(m)

folium.Marker(
    user_loc, popup="📍 Your Location",
    icon=folium.Icon(color='red', icon='star', prefix='fa')
).add_to(m)

for _, row in df.iterrows():
    popup = f"""
    <div style="width:220px;font-family:Inter;">
        <h4 style="margin:0 0 8px 0;">{row['Name']}</h4>
        <p><b>Type:</b> {row['Type']}</p>
        <p><b>Distance:</b> {row['Distance_km']} km</p>
        <p><b>Phone:</b> {row['Phone']}</p>
        <p><b>Address:</b> {row['Address']}</p>
        <div style="margin-top:10px;">
            <a href="{row['Google_Maps']}" target="_blank" 
               style="background:#10b981;color:white;padding:6px 12px;text-decoration:none;
                      border-radius:6px;margin-right:5px;display:inline-block;font-size:0.8rem;">Map</a>
            <a href="{row['Directions']}" target="_blank" 
               style="background:#3b82f6;color:white;padding:6px 12px;text-decoration:none;
                      border-radius:6px;display:inline-block;font-size:0.8rem;">Directions</a>
        </div>
    </div>
    """
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup, max_width=250),
        tooltip=f"{row['Name']} ({row['Distance_km']} km)",
        icon=folium.Icon(color=colors.get(row['Type'], 'gray'),
                         icon=icons.get(row['Type'], 'info-sign'), prefix='fa')
    ).add_to(marker_cluster)

folium.Circle(
    user_loc, radius=radius_km*1000, color='#667eea', fill=True, fillOpacity=0.1
).add_to(m)

folium_static(m, width=1200, height=500)

# --- Table View ---
st.markdown('<h2 style="margin-top:30px;">📋 Results</h2>', unsafe_allow_html=True)
st.dataframe(df[['Name', 'Type', 'Distance_km', 'Address', 'Phone']])
