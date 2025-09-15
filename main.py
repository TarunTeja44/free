import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

st.title("Nearby Free Resources Finder")

# User inputs
place_name = st.text_input("Enter your location (city/area/sub-area):")
radius_km = st.number_input("Enter search radius in km:", min_value=1, max_value=50, value=10)

resource_types = {
    "Hospital": 'amenity=hospital',
    "Library": 'amenity=library',
    "WiFi": 'internet_access=wlan',
    "Food/Drinks": 'amenity=restaurant',
    "Water": 'amenity=drinking_water',
    "Food Donation": 'charity=food'
}

if st.button("Find Nearby Resources"):
    if not place_name.strip():
        st.error("Please enter a location!")
    else:
        # Get coordinates of user location
        geolocator = Nominatim(user_agent="free_resources_finder")
        location = geolocator.geocode(place_name)
        
        if location:
            user_location = (location.latitude, location.longitude)
            st.success(f"Location found: {location.address}")
            
            all_results = []

            # Function to query Overpass API
            def query_osm(lat, lon, radius_m, tag):
                overpass_url = "http://overpass-api.de/api/interpreter"
                query = f"""
                [out:json];
                node(around:{radius_m},{lat},{lon})[{tag}];
                out center;
                """
                response = requests.get(overpass_url, params={'data': query})
                data = response.json()
                results = []
                for element in data['elements']:
                    name = element['tags'].get('name', 'Unknown')
                    results.append({
                        'Name': name,
                        'Type': tag.split('=')[0].capitalize(),
                        'Latitude': element.get('lat', None),
                        'Longitude': element.get('lon', None)
                    })
                return results

            # Query each resource type
            for r_type, tag in resource_types.items():
                results = query_osm(location.latitude, location.longitude, radius_km*1000, tag)
                for r in results:
                    r['Type'] = r_type  # Set proper type name
                    # Calculate distance
                    if r['Latitude'] and r['Longitude']:
                        r['Distance_km'] = round(geodesic(user_location, (r['Latitude'], r['Longitude'])).km, 2)
                    else:
                        r['Distance_km'] = None
                    all_results.append(r)

            # Display results
            if not all_results:
                st.write("No nearby resources found!")
            else:
                df = pd.DataFrame(all_results)
                df = df.sort_values(by='Distance_km')
                st.dataframe(df[['Name','Type','Distance_km']])
        else:
            st.error("Location not found. Please enter a valid city/area/sub-area.")
