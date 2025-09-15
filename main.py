import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Sample data: Free resources
data = {
    'Name': ['City Library', 'College WiFi Spot', 'Community Cafe', 'Student Study Hall'],
    'Type': ['Library', 'WiFi', 'Food/Drinks', 'Study Space'],
    'Latitude': [17.3850, 17.3870, 17.3890, 17.3820],
    'Longitude': [78.4867, 78.4880, 78.4820, 78.4840]
}

df = pd.DataFrame(data)

st.title("Nearby Free Resources Finder")

# User enters place name
place_name = st.text_input("Enter your location (city/area/sub-area):", "Hyderabad")

if st.button("Find Nearby Resources"):
    geolocator = Nominatim(user_agent="free_resources_finder")
    location = geolocator.geocode(place_name)

    if location:
        user_location = (location.latitude, location.longitude)
        st.success(f"Location found: {location.address}")

        # Filter resources within 2 km
        def nearby_resources(df, user_location, radius_km=2):
            resources = []
            for index, row in df.iterrows():
                resource_location = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_location, resource_location).km
                if distance <= radius_km:
                    resources.append({**row, 'Distance_km': round(distance, 2)})
            return pd.DataFrame(resources)

        nearby_df = nearby_resources(df, user_location)

        st.subheader("Nearby Resources within 2 km")
        if nearby_df.empty:
            st.write("No nearby free resources found!")
        else:
            st.dataframe(nearby_df)

        # Display map
        m = folium.Map(location=user_location, zoom_start=15)
        folium.Marker(location=user_location, popup="You are here", icon=folium.Icon(color='blue')).add_to(m)

        for index, row in nearby_df.iterrows():
            folium.Marker(
                location=(row['Latitude'], row['Longitude']),
                popup=f"{row['Name']} ({row['Type']}) - {row['Distance_km']} km",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)

        st.subheader("Map View")
        st_folium(m, width=700, height=500)
    else:
        st.error("Location not found. Please enter a valid city/area/sub-area.")
