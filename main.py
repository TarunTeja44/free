import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import time

st.title("Hospital and Police Station Finder - India")

# User input
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        try:
            # Step 1: Get user coordinates
            geolocator = Nominatim(user_agent="india_hospital_police_finder")
            location = geolocator.geocode(place_name, timeout=10)
            
            if not location:
                st.error("Location not found. Try a more specific city/area/sub-area.")
            else:
                user_location = (location.latitude, location.longitude)
                st.success(f"Coordinates found: {location.latitude}, {location.longitude}")
                
                # Step 2: Define resource queries
                resource_queries = {
                    "Hospital": '[amenity=hospital]',
                    "Medical Camps": '[healthcare=clinic][charity=yes]',
                    "Police Station": '[amenity=police]'
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
                            
                            # Determine hospital type
                            final_type = r_type
                            if r_type == "Hospital":
                                operator = element['tags'].get('operator', '').lower()
                                if "government" in operator:
                                    final_type = "Government Hospital"
                                elif "private" in operator:
                                    final_type = "Private Hospital"
                                else:
                                    final_type = "Hospital (Unknown Type)"
                            
                            # Get accurate location: use OSM tags first, fallback to reverse geocode
                            tags = element.get('tags', {})
                            area = tags.get('addr:full') or tags.get('addr:street') or tags.get('addr:city') or tags.get('addr:suburb') or tags.get('addr:state')
                            if not area and rlat and rlon:
                                try:
                                    loc = geolocator.reverse((rlat, rlon), timeout=10)
                                    area = loc.address if loc else "Unknown"
                                    time.sleep(1)  # Only sleep when reverse geocoding
                                except:
                                    area = "Unknown"
                            elif not area:
                                area = "Unknown"
                            
                            all_results.append({
                                'Name': name,
                                'Type': final_type,
                                'Distance_km': distance,
                                'Location': area
                            })
                    except:
                        st.warning(f"Error fetching {r_type} data from OpenStreetMap.")
                
                # Step 3: Display results with search
                if not all_results:
                    st.info("No nearby resources found!")
                else:
                    df = pd.DataFrame(all_results)
                    df = df.sort_values(by='Distance_km')
                    st.subheader(f"Nearby Resources within {radius_km} km")
                    
                    search_term = st.text_input("Search in results:")
                    if search_term:
                        df_filtered = df[df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().to_string(), axis=1)]
                        st.dataframe(df_filtered[['Name','Type','Distance_km','Location']])
                    else:
                        st.dataframe(df[['Name','Type','Distance_km','Location']])
                    
                    # Notify missing categories
                    categories = ["Government Hospital","Private Hospital","Hospital (Unknown Type)","Medical Camps","Police Station"]
                    for cat in categories:
                        if not any(df['Type'] == cat):
                            st.info(f"No {cat} found near your location.")
        except Exception:
            st.error("Unable to fetch location or resources. Please try again later.")
