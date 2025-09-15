# Resource queries
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
            
            # Use OSM address tags for location
            tags = element.get('tags', {})
            area = tags.get('addr:full') or tags.get('addr:street') or tags.get('addr:city') or tags.get('addr:suburb') or tags.get('addr:state') or "Unknown"
            
            all_results.append({
                'Name': name,
                'Type': final_type,
                'Distance_km': distance,
                'Location': area
            })
    except:
        st.warning(f"Error fetching {r_type} data from OpenStreetMap.")
