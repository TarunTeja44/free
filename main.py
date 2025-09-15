import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Extended dataset: Free resources
data = {
    'Name': [
        'State Central Library', 
        'Govt. General Hospital', 
        'NGO Helping Hands', 
        'Free Food Center', 
        'Water Point – Community Service', 
        'Student Study Hall'
    ],
    'Type': [
        'Library', 
        'Government Hospital', 
        'NGO', 
        'Free Food', 
        'Free Water', 
        'Study Space'
    ],
    'Latitude': [17.3850, 17.3875, 17.3905, 17.3830, 17.3862, 17.3820],
    'Longitude': [78.4867, 78.4890, 78.4815, 78.4855, 78.4875, 78.4840]
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

        # Function to find resources within a radius
        def nearby_resources(df, user_location, radius_km=3):
            resources = []
            for index, row in df.iterrows():
                resource_location = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_location, resource_location).km
                if distance <= radius_km:
                    resources.append({**row, 'Distance_km': round(distance, 2)})
            return pd.DataFrame(resources)

        nearby_df = nearby_resources(df, user_location)

        st.subheader("Nearby Free Resources (within 3 km)")
        if nearby_df.empty:
            st.warning("No nearby free resources found!")
        else:
            st.dataframe(nearby_df)

            # Create map
            m = folium.Map(location=user_location, zoom_start=14)

            # Add user marker
            folium.Marker(
                location=user_location, 
                popup="You are here", 
                icon=folium.Icon(color='blue', icon="user")
            ).add_to(m)

            # Add resource markers
            for index, row in nearby_df.iterrows():
                folium.Marker(
                    location=(row['Latitude'], row['Longitude']),
                    popup=f"<b>{row['Name']}</b><br>{row['Type']}<br>{row['Distance_km']} km",
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)

            # Auto fit map to show all points
            bounds = [(row['Latitude'], row['Longitude']) for _, row in nearby_df.iterrows()]
            bounds.append(user_location)
            m.fit_bounds(bounds)

            st.subheader("Map View")
            st_folium(m, width=750, height=500)
    else:
        st.error("Location not found. Please enter a valid city/area/sub-area.")
