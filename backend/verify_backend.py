import requests
import sys
import os

# Set the API key in environment for testing if not already set
# (In a real run, this would be picked up from .env by the server)
# But here we are testing the server logic, so we'll try to import the function directly if possible,
# or just run the server and hit the endpoint.

# Let's try to run the server in a separate process and hit it?
# Or simpler: Import the function and test it.

sys.path.append('/Users/vidishadeswal/currencychanger/backend')
from server import fetch_google_aqi, process_google_aqi

print("Testing fetch_google_aqi...")
# We expect this to fail or return error dict because of billing, but it should not crash.
data = fetch_google_aqi()
print(f"Fetch result: {data}")

if data and 'error' in data:
    print("API returned error as expected (billing).")
elif data:
    print("API returned data!")
else:
    print("API returned None (likely due to missing key or network error).")

print("\nTesting process_google_aqi with mock data...")
mock_data = {
    "indexes": [
        {
            "code": "uaqi",
            "displayName": "Universal AQI",
            "aqi": 42,
            "category": "Good"
        }
    ],
    "pollutants": [
        {
            "code": "pm25",
            "concentration": {
                "value": 12.5,
                "units": "µg/m³"
            }
        }
    ]
}

processed = process_google_aqi(mock_data)
print(f"Processed result: {processed}")

if processed['val'] == 42 and processed['status'] == "Good" and processed['pm25'] == 12.5:
    print("Processing logic verification passed.")
else:
    print("Processing logic verification FAILED.")
