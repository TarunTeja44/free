import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic

st.title("Nearby Free Resources Finder")

# User inputs
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        # Step 1: Use Overpass to find approximate coordinates of the place
        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            query_location = f"""
            [out:json];
            area["name"="{place_name}"];
            out center;
            """
            response = requests.get(overpass_url, params={'data': query_location}, timeout=30)
            data = response.json()
            elements = data.get('elements', [])
            if not elements:
                st.error("Location not found in OpenStreetMap. Try a more specific area.")
            else:
                # Use first matching area
                element = elements[0]
                lat = element.get('lat') or element.get('center', {}).get('lat')
                lon = element.get('lon') or element.get('center', {}).get('lon')
                if not lat or not lon:
                    st.error("Could not determine coordinates of the location.")
                else:
                    user_location = (lat, lon)
                    st.success(f"Approximate coordinates found: {lat}, {lon}")
                    
                    # Step 2: Query resources within radius
                    resource_queries = {
                        "Government Hospital": '[amenity=hospital][operator~"government|Government"]',
                        "Other Hospitals": '[amenity=hospital][!operator]',
                        "Free Food": '[charity=food]',
                        "Free Water": '[amenity=drinking_water]',
                        "Medical Camps": '[healthcare=clinic][charity=yes]'
                    }
                    
                    all_results = []
                    
                    for r_type, tag in resource_queries.items():
                        query_resource = f"""
                        [out:json];
                        node(around:{radius_km*1000},{lat},{lon}){tag};
                        out center;
                        """
                        try:
                            res_response = requests.get(overpass_url, params={'data': query_resource}, timeout=30)
                            res_data = res_response.json()
                            for element in res_data.get('elements', []):
                                name = element['tags'].get('name', 'Unknown')
                                rlat = element.get('lat')
                                rlon = element.get('lon')
                                # Distance
                                distance = round(geodesic(user_location, (rlat, rlon)).km, 2) if rlat and rlon else None
                                # Area/Address approximation
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
                        categories = ["Government Hospital","Other Hospitals","Free Food","Free Water","Medical Camps"]
                        for cat in categories:
                            if not any(df['Type'] == cat):
                                st.info(f"No {cat} found near your location.")
        except Exception as e:
            st.error("Unable to fetch location or resources. Please try again later.")
