import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("Nearby Government Hospitals Finder")

# User inputs
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Government Hospitals"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        geolocator = Nominatim(user_agent="gov_hospital_finder")
        location = geolocator.geocode(place_name)
        
        if location:
            user_location = (location.latitude, location.longitude)
            st.success(f"Location found: {location.address}")
            
            all_results = []

            # Query Overpass API for government hospitals
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            node(around:{radius_km*1000},{location.latitude},{location.longitude})[amenity=hospital][operator~"government|Government"];
            out center;
            """
            try:
                response = requests.get(overpass_url, params={'data': query}, timeout=30)
                data = response.json()
                for element in data.get('elements', []):
                    name = element['tags'].get('name', 'Unknown')
                    lat = element.get('lat', None)
                    lon = element.get('lon', None)
                    # Reverse geocode to get area
                    try:
                        loc = geolocator.reverse((lat, lon), exactly_one=True, timeout=10)
                        area = loc.address if loc else "Unknown"
                    except:
                        area = "Unknown"
                    # Distance from user location
                    distance = round(geodesic(user_location, (lat, lon)).km, 2) if lat and lon else None
                    all_results.append({
                        'Name': name,
                        'Type': 'Government Hospital',
                        'Distance_km': distance,
                        'Location': area
                    })
            except:
                st.error("Error fetching data from OpenStreetMap.")

            # Display results
            if not all_results:
                st.info("No government hospitals found near your location.")
            else:
                df = pd.DataFrame(all_results)
                df = df.sort_values(by='Distance_km')
                st.subheader(f"Government Hospitals within {radius_km} km")
                st.dataframe(df[['Name','Type','Distance_km','Location']])
        else:
            st.error("Location not found. Please enter a valid city/area/sub-area.")
