import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("Hospital and Police Station Finder - India (Optimized)")

# --- User Input ---
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        try:
            # --- Get Coordinates ---
            geolocator = Nominatim(user_agent="hospital_police_finder")
            location = geolocator.geocode(place_name, timeout=10)
            if not location:
                st.error("Location not found. Try a more specific area.")
            else:
                user_location = (location.latitude, location.longitude)
                st.success(f"Coordinates: {location.latitude}, {location.longitude}")

                # --- Define Resources ---
                resource_queries = {
                    "Hospital": '[amenity=hospital]',
                    "Medical Camp": '[healthcare=clinic][charity=yes]',
                    "Police Station": '[amenity=police]'
                }

                all_results = []
                overpass_url = "http://overpass-api.de/api/interpreter"

                # --- Fetch Resources ---
                for r_type, tag in resource_queries.items():
                    # Optimized single-line query, fetch only top 50 nodes
                    query_resource = f'[out:json][timeout:25];node(around:{radius_km*1000},{location.latitude},{location.longitude}){tag};out center 50;'
                    
                    try:
                        res = requests.get(overpass_url, params={'data': query_resource}, timeout=30)
                        data = res.json()
                        
                        for element in data.get('elements', []):
                            name = element['tags'].get('name', 'Unknown')
                            rlat = element.get('lat')
                            rlon = element.get('lon')
                            distance = round(geodesic(user_location, (rlat, rlon)).km, 2) if rlat and rlon else None

                            # --- Determine Hospital Type ---
                            final_type = r_type
                            if r_type == "Hospital":
                                operator = element['tags'].get('operator', '').lower()
                                if "private" in operator:
                                    final_type = "Private Hospital"
                                else:
                                    # If operator missing, assume Government Hospital
                                    final_type = "Government Hospital"

                            # --- Get Location from tags ---
                            tags = element.get('tags', {})
                            area = tags.get('addr:full') or tags.get('addr:street') or tags.get('addr:city') \
                                   or tags.get('addr:suburb') or tags.get('addr:state') or "Unknown"

                            all_results.append({
                                'Name': name,
                                'Type': final_type,
                                'Distance_km': distance,
                                'Location': area
                            })

                    except:
                        st.warning(f"Error fetching {r_type} data from OpenStreetMap.")

                # --- Display Results ---
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

                    # --- Notify missing categories ---
                    categories = ["Government Hospital","Private Hospital","Medical Camp","Police Station"]
                    for cat in categories:
                        if not any(df['Type'] == cat):
                            st.info(f"No {cat} found near your location.")

        except Exception as e:
            st.error("Unable to fetch resources. Please try again later.")
