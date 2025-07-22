import requests
import streamlit as st
import os
from dotenv import load_dotenv
import openrouteservice

# Load from Streamlit secrets (Cloud)
ORS_API_KEY = st.secrets.get("ORS_API_KEY")

# Fallback to local .env for dev
if ORS_API_KEY is None:
    load_dotenv()
    ORS_API_KEY = os.getenv("ORS_API_KEY")

if ORS_API_KEY is None:
    st.error("ORS API key not found!")
else:
    client = openrouteservice.Client(key=ORS_API_KEY)



# ✅ Function to convert a place name or full address into coordinates
def get_coordinates(place_name):
    """
    Given a place name or full address, returns [longitude, latitude] using ORS geocoding.
    """
    url = "https://api.openrouteservice.org/geocode/search"
    
    params = {
        "api_key": ORS_API_KEY,  # Required key to access the API
        "text": place_name,      # Address or place to search
        "size": 1                # Get only the best/top match
    }

    # 📡 Sending GET request to ORS API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # ✅ If request is successful, extract the coordinates
        data = response.json()
        features = data.get("features", [])
        
        if features:
            coordinates = features[0]['geometry']['coordinates']  # Format: [lon, lat]
            return coordinates
        else:
            print(f"❌ No coordinates found for: {place_name}")
            return None
    else:
        print(f"⚠️ Error {response.status_code}: Could not fetch data for {place_name}")
        return None
    
def get_distance(coord1, coord2):
    """
    Calculate real-world travel distance (in km) between two coordinates using ORS Directions API.
    coord1 and coord2 should be in format [longitude, latitude]
    """
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [coord1, coord2]
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        data = response.json()
        distance_meters = data['routes'][0]['summary']['distance']
        distance_km = round(distance_meters / 1000, 2)
        return distance_km
    else:
        print(f"Error fetching distance: {response.status_code}")
        return None

if __name__ == "__main__":
    address = input("Enter full address: ")
    coords = get_coordinates(address)
    print("Coordinates:", coords)
if __name__ == "__main__":
    place1 = "Pathankot, Punjab, 145001"
    place2 = "Kathua, Jammu and kashmir, 184101"

    coord1 = get_coordinates(place1)
    coord2 = get_coordinates(place2)

    if coord1 and coord2:
        distance = get_distance(coord1, coord2)
        print(f"Distance between {place1} and {place2} is {distance} km")
