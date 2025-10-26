from folium.plugins import MarkerCluster

# Updated colors & icons for better clarity
colors = {
    'Hospital': 'red', 'Clinic': 'pink', 'Doctors': 'purple',
    'Pharmacy': 'green', 'Police Station': 'blue', 'Fire Station': 'orange',
    'ATM': 'darkpurple', 'Embassy': 'lightgray', 'Tourist Office': 'cadetblue'
}

icons = {
    'Hospital': 'plus-square', 'Clinic': 'stethoscope', 'Doctors': 'user-md',
    'Pharmacy': 'prescription-bottle', 'Police Station': 'shield-alt', 'Fire Station': 'fire-extinguisher',
    'ATM': 'money-bill', 'Embassy': 'university', 'Tourist Office': 'info-circle'
}

# Map
st.markdown('<div class="section-header">🗺️ Interactive Map</div>', unsafe_allow_html=True)
m = folium.Map(location=user_loc, zoom_start=13)

# Cluster for performance
marker_cluster = MarkerCluster().add_to(m)

# User location
folium.Marker(
    user_loc, popup="Your Location",
    icon=folium.Icon(color='red', icon='star', prefix='fa')
).add_to(m)

for _, row in df.iterrows():
    # Graceful handling
    phone = row['Phone'] if row['Phone'] not in ['N/A', '', None] else 'Not available'
    address = row['Address'] if row['Address'] not in ['N/A', '', None] else 'Address not available'

    popup = f"""
    <div style="width:220px;font-family:Inter;">
        <h4 style="margin:0 0 8px 0;">{row['Name']}</h4>
        <p style="margin:3px 0;font-size:0.85rem;"><b>Type:</b> {row['Type']}</p>
        <p style="margin:3px 0;font-size:0.85rem;"><b>Distance:</b> {row['Distance_km']} km</p>
        <p style="margin:3px 0;font-size:0.85rem;"><b>Phone:</b> {phone}</p>
        <p style="margin:3px 0;font-size:0.85rem;"><b>Address:</b> {address}</p>
        <div style="margin-top:10px;">
            <a href="{row['Google_Maps']}" target="_blank" 
               style="background:#10b981;color:white;padding:6px 12px;text-decoration:none;
                      border-radius:6px;margin-right:5px;display:inline-block;font-size:0.8rem;">Map</a>
            <a href="{row['Directions']}" target="_blank" 
               style="background:#3b82f6;color:white;padding:6px 12px;text-decoration:none;
                      border-radius:6px;display:inline-block;font-size:0.8rem;">Directions</a>
        </div>
    </div>"""
    
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup, max_width=250),
        tooltip=f"{row['Name']} ({row['Distance_km']} km)",
        icon=folium.Icon(color=colors.get(row['Type'], 'gray'),
                         icon=icons.get(row['Type'], 'info-sign'), prefix='fa')
    ).add_to(marker_cluster)

folium.Circle(
    user_loc, radius=radius_km*1000, color='#667eea', fill=True, fillOpacity=0.1
).add_to(m)

folium_static(m, width=1200, height=500)
