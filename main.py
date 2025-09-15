import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.title("Nearby Free Resources Finder")

# Sample dataset across multiple cities for demo
data = {
    'Name': [
        'City Library Hyderabad', 'College WiFi Hyderabad', 
        'Government Hospital Delhi', 'Food Donation Center Delhi', 
        'Free Water Point Mumbai', 'Community Cafe Mumbai'
    ],
    'Type': ['Library', 'WiFi', 'Hospital', 'Food/Drinks', 'Water', 'Food/Drinks'],
    'Latitude': [17.3850, 17.3870, 28.6139, 28.6200, 19.0760, 19.0800],
    'Longitude': [78.4867, 78.4880, 77.2090, 77.2100, 72.8777, 72.8800]
}

df = pd.DataFrame(data)

# User input
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

            # Find resources within radius
            resources = []
            for index, row in df.iterrows():
                resource_location = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_location, resource_location).km
                if distance <= radius_km:
                    try:
                        loc = geolocator.reverse(resource_location, exactly_one=True, timeout=10)
                        area = loc.address if loc else "Unknown"
                    except:
                        area = "Unknown"
                    resources.append({
                        'Name': row['Name'],
                        'Type': row['Type'],
                        'Distance_km': round(distance, 2),
                        'Area': area
                    })
            
            nearby_df = pd.DataFrame(resources)
            st.subheader(f"Nearby Free Resources within {radius_km} km")
            if nearby_df.empty:
                st.write("No nearby free resources found!")
            else:
                st.dataframe(nearby_df.sort_values(by='Distance_km'))
        else:
            st.error("Location not found. Please enter a valid city/area/sub-area.")
