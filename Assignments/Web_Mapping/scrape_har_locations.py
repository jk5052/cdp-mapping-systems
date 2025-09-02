import json
import requests
import folium
from folium.plugins import MarkerCluster
from typing import List, Tuple

# === CONFIGURATION ===
HAR_FILE = "www.airbnb.com.har"
OUTPUT_MAP = "airbnb_ip_map.html"
MAX_IPS = 50

# === FUNCTIONS ===
def load_ips_from_har(path: str) -> List[Tuple[str, str]]:
    """Extract unique IP addresses from a HAR file."""
    with open(path, "r", encoding="utf-8") as f:
        har = json.load(f)
    
    entries = har.get("log", {}).get("entries", [])
    ips = set()
    
    for entry in entries:
        ip = entry.get("serverIPAddress")
        url = entry.get("request", {}).get("url", "")
        print(f"Processing entry: {url[:50]}... with IP: {ip}")
        
        if ip:
            # Remove brackets from IPv6 addresses
            ip = ip.strip("[]")
            ips.add((ip, url))
    
    return list(ips)

def geolocate_ip(ip_item: Tuple[str, str]) -> Tuple[str, float, float, str]:
    """Geolocate IP address using ip-api.com API."""
    ip, url = ip_item
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = resp.json()
        
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            print(f"Located {ip}: {lat}, {lon}")
            return ip, lat, lon, url
    except Exception as e:
        print(f"Error geolocating {ip}: {e}")
    
    return ip, 0, 0, url

def build_map(ip_locations: List[Tuple[str, float, float, str]], output_path: str) -> None:
    """Generate Folium map from list of IP + lat/lon tuples."""
    # Start with world map view
    m = folium.Map(location=[20, 0], zoom_start=2)
    cluster = MarkerCluster().add_to(m)
    
    for ip, lat, lon, url in ip_locations:
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"IP: {ip}<br>URL: {url[:50]}...",
                icon=folium.Icon(color="red", icon="home"),
            ).add_to(cluster)
    
    # Create GeoJSON data
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ip": ip, "url": url},
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],
                },
            }
            for ip, lat, lon, url in ip_locations
            if lat and lon
        ],
    }
    
    # Save map
    m.save(output_path)
    print(f"Map saved to: {output_path}")
    
    # Save GeoJSON file
    with open("airbnb_locations.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print("GeoJSON saved to: airbnb_locations.geojson")

# === RUN ===
if __name__ == "__main__":
    print("🏠 Starting Airbnb HAR file analysis...")
    
    # Extract IP list from HAR file
    ip_list = load_ips_from_har(HAR_FILE)
    print(f"Found {len(ip_list)} IPs")
    
    # Deduplicate IPs
    ips_dict = {}
    for ip, url in ip_list:
        if ip not in ips_dict:
            ips_dict[ip] = url
    
    ips = list(ips_dict.items())
    print(f"Unique IPs: {len(ips)}")
    
    # Geolocate IPs
    print("🌍 Geolocating IPs...")
    ip_locations = [geolocate_ip(ip) for ip in ips[:MAX_IPS]]
    print(f"Geolocated {len(ip_locations)} IPs")
    
    # Build map
    print("🗺️ Building map...")
    build_map(ip_locations, OUTPUT_MAP)
    
    print("✅ Complete! Check these files:")
    print(f"   - {OUTPUT_MAP} (HTML map)")
    print(f"   - airbnb_locations.geojson (GeoJSON data)")