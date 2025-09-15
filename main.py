import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("Nearby Free Resources Finder - India")

# User input
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        try:
            # Step 1: Get coordinates using Nominatim
            geolocator = Nominatim(user_agent="india_free_resources")
            location = geolocator.geocode(place_name, timeout=10)
            
            if not location:
                st.error("Location not found. Try a more specific city/area/sub-area.")
            else:
                user_location = (location.latitude, location.longitude)
                st.success(f"Coordinates found: {location.latitude}, {location.longitude}")
                
                # Step 2: Define resource queries
                resource_queries = {
                    "Government Hospital": '[amenity=hospital][operator~"government|Government"]',
                    "Other Hospitals": '[amenity=hospital][!operator]',
                    "Free Food": '[charity=food]',
                    "Free Water": '[amenity=drinking_water]',
                    "Medical Camps": '[healthcare=clinic][charity=yes]',
                    "Free Wi-Fi": '[internet_access=wlan]'
                }
                
                all_results = []
                overpass_url = "http://overpass-api.de/api/interpreter"
                
                for r_type, tag in resource_queries.items():
                    query_resource = f"""
                    [out:json];
                    node(around:{radius_km*1000},{location.latitude},{location.longitude}){tag};
                    out center;
                    """
                    try:
                        res_response = requests.get(overpass_url, params={'data': query_resource}, timeout=30)
                        res_data = res_response.json()
                        for element in res_data.get('elements', []):
                            name = element['tags'].get('name', 'Unknown')
                            rlat = element.get('lat')
                            rlon = element.get('lon')
                            distance = round(geodesic(user_location, (rlat, rlon)).km, 2) if rlat and rlon else None
                            area = element['tags'].get('addr:full') or element['tags'].get('addr:city') or "Unknown"
                            all_results.append({
                                'Name': name,
                                'Type': r_type,
                                'Distance_km': distance,
                                'Location': area
                            })
                    except:
                        st.warning(f"Error fetching {r_type} data from OpenStreetMap.")
                
                # Step 3: Display results
                if not all_results:
                    st.info("No nearby free resources found!")
                else:
                    df = pd.DataFrame(all_results)
                    df = df.sort_values(by='Distance_km')
                    st.subheader(f"Nearby Free Resources within {radius_km} km")
                    st.dataframe(df[['Name','Type','Distance_km','Location']])
                    
                    # Notify missing categories
                    categories = ["Government Hospital","Other Hospitals","Free Food","Free Water","Medical Camps","Free Wi-Fi"]
                    for cat in categories:
                        if not any(df['Type'] == cat):
                            st.info(f"No {cat} found near your location.")
        except Exception:
            st.error("Unable to fetch location or resources. Please try again later.")
