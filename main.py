import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("🚨 Hospital & Police Station Finder - India")

# --- User Input ---
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        try:
            geolocator = Nominatim(user_agent="hospital_police_finder")
            location = geolocator.geocode(place_name, timeout=10)
            if not location:
                st.error("Location not found. Try a more specific area.")
            else:
                user_location = (location.latitude, location.longitude)
                st.success(f"✅ Location found: {location.address}")

                # --- Define Queries ---
                resource_queries = {
                    "Hospital": '[amenity=hospital]',
                    "Medical Camp": '[healthcare=clinic][charity=yes]',
                    "Police Station": '[amenity=police]',
                    "Pharmacy": '[amenity=pharmacy]',
                    "Fire Station": '[amenity=fire_station]',
                    "Ambulance": '[emergency=ambulance_station]'
                }

                all_results = []
                overpass_url = "http://overpass-api.de/api/interpreter"

                for r_type, tag in resource_queries.items():
                    try:
                        query_resource = f'[out:json][timeout:25];node(around:{radius_km*1000},{location.latitude},{location.longitude}){tag};out center 50;'
                        res = requests.get(overpass_url, params={'data': query_resource}, timeout=30)
                        data = res.json()

                        for element in data.get('elements', []):
                            name = element['tags'].get('name', 'Unknown')
                            rlat = element.get('lat')
                            rlon = element.get('lon')
                            distance = round(geodesic(user_location, (rlat, rlon)).km, 2) if rlat and rlon else None

                            # Try to get a clean address
                            tags = element.get('tags', {})
                            address_parts = [
                                tags.get('addr:housename'),
                                tags.get('addr:housenumber'),
                                tags.get('addr:street'),
                                tags.get('addr:suburb'),
                                tags.get('addr:city'),
                                tags.get('addr:state')
                            ]
                            area = ', '.join([a for a in address_parts if a])
                            if not area:
                                area = "Address not available"

                            # --- Google Maps Link ---
                            if rlat and rlon:
                                maps_link = f"https://www.google.com/maps?q={rlat},{rlon}"
                            else:
                                maps_link = "N/A"

                            all_results.append({
                                'Name': name,
                                'Type': r_type,
                                'Distance (km)': distance,
                                'Address': area,
                                'Google Maps': f"[Open Map]({maps_link})"
                            })
                    except Exception as e:
                        st.warning(f"Error fetching {r_type} data: {e}")

                # --- Display Results ---
                if not all_results:
                    st.info("No nearby resources found!")
                else:
                    df = pd.DataFrame(all_results)
                    df = df.sort_values(by='Distance (km)')
                    st.subheader(f"Nearby Resources within {radius_km} km")
                    st.markdown("Click **Open Map** to view on Google Maps 🌍")
                    st.write(df.to_markdown(index=False), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Unable to fetch resources. {e}")
