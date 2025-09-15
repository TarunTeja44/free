import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("Nearby Free Resources Finder")

# User inputs
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        geolocator = Nominatim(user_agent="free_resources_finder")
        location = geolocator.geocode(place_name)
        
        if location:
            user_location = (location.latitude, location.longitude)
            st.success(f"Location found: {location.address}")
            
            all_results = []

            # Define resource types and corresponding OSM tags
            resource_queries = {
                "Government Hospital": '[amenity=hospital][operator~"government|Government"]',
                "Other Hospitals": '[amenity=hospital][!operator]',  # Hospitals without government operator tag
                "Free Food": '[charity=food]',
                "Free Water": '[amenity=drinking_water]',
                "Medical Camps": '[healthcare=clinic][charity=yes]'  # Approximation
            }

            overpass_url = "http://overpass-api.de/api/interpreter"

            for r_type, tag in resource_queries.items():
                query = f"""
                [out:json];
                node(around:{radius_km*1000},{location.latitude},{location.longitude}){tag};
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
                            'Type': r_type,
                            'Distance_km': distance,
                            'Location': area
                        })
                except:
                    st.warning(f"Error fetching {r_type} data from OpenStreetMap.")

            # Display results
            if not all_results:
                st.info("No nearby free resources found!")
            else:
                df = pd.DataFrame(all_results)
                df = df.sort_values(by='Distance_km')
                st.subheader(f"Nearby Free Resources within {radius_km} km")
                st.dataframe(df[['Name','Type','Distance_km','Location']])
                
                # Notify if a category is missing
                categories = ["Government Hospital","Other Hospitals","Free Food","Free Water","Medical Camps"]
                for cat in categories:
                    if not any(df['Type'] == cat):
                        st.info(f"No {cat} found near your location.")

        else:
            st.error("Location not found. Please enter a valid city/area/sub-area.")
