import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.title("Nearby Free Resources Finder")

# Sample dataset
data = {
    'Name': [
        'City Library', 'College WiFi Spot', 'Community Cafe', 'Student Study Hall',
        'Government Hospital', 'Food Donation Center', 'Free Water Point'
    ],
    'Type': [
        'Library', 'WiFi', 'Food/Drinks', 'Study Space',
        'Hospital', 'Food/Drinks', 'Water'
    ],
    'Latitude': [17.3850, 17.3870, 17.3890, 17.3820, 17.3860, 17.3840, 17.3830],
    'Longitude': [78.4867, 78.4880, 78.4820, 78.4840, 78.4870, 78.4850, 78.4830]
}

df = pd.DataFrame(data)

# User input for location
place_name = st.text_input("Enter your location (city/area/sub-area):", "Hyderabad")

if st.button("Find Nearby Resources"):
    geolocator = Nominatim(user_agent="free_resources_finder")
    location = geolocator.geocode(place_name)

    if location:
        user_location = (location.latitude, location.longitude)
        st.success(f"Location found: {location.address}")

        # Find nearby resources within 2 km
        def nearby_resources(df, user_location, radius_km=2):
            resources = []
            for index, row in df.iterrows():
                resource_location = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_location, resource_location).km
                if distance <= radius_km:
                    resources.append({**row, 'Distance_km': round(distance, 2)})
            return pd.DataFrame(resources)

        nearby_df = nearby_resources(df, user_location)

        st.subheader("Nearby Free Resources within 2 km")
        if nearby_df.empty:
            st.write("No nearby free resources found!")
        else:
            # Display sorted by distance
            nearby_df = nearby_df.sort_values(by='Distance_km')
            st.dataframe(nearby_df[['Name', 'Type', 'Distance_km']])
    else:
        st.error("Location not found. Please enter a valid city/area/sub-area.")
