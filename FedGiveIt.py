import requests
import json
import xml.etree.ElementTree as ET
from API_tokens import FEDFRED_TOKEN

# Define the base URL for the FRED API
base_url = "https://api.stlouisfed.org/fred/"

# Replace "YOUR_API_KEY" with your actual API key from the St. Louis Fed website
api_key = FEDFRED_TOKEN

# Function to retrieve data from the API and return a formatted JSON response
def get_data(endpoint, params):
    params["api_key"] = api_key
    response = requests.get(base_url + endpoint, params=params)
    print("API request URL:", response.url)  # Print the API request URL for debugging

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type")
        if "application/json" in content_type:
            return json.loads(response.text)
        elif "application/xml" in content_type or "text/xml" in content_type:
            return parse_xml_response(response.text)
        else:
            print(f"Unsupported content type: {content_type}")
            return None
    else:
        print(f"Error retrieving data. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return None

def parse_xml_response(xml_text):
    root = ET.fromstring(xml_text)
    data = []
    for observation in root.findall("observation"):
        date = observation.get("date")
        value = observation.get("value")
        data.append({"date": date, "value": value})
    return data

def display_data(data_list):
    if data_list and isinstance(data_list, list) and len(data_list) > 0:
        print("Date\t\tValue")
        print("----------------------")
        for data in data_list:
            print(f"{data['date']}\t{data['value']}")
    else:
        print("No data available.")

def get_series_data(series_id, start_date, end_date):
    endpoint = "series/observations"
    params = {
        "series_id": series_id,
        "observation_start": start_date,
        "observation_end": end_date,
    }
    data_list = get_data(endpoint, params)
    return data_list

if __name__ == "__main__":
    series_id = input("Enter the series ID (e.g., UNRATE, GS10): ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    key_indicators_data = get_series_data(series_id, start_date, end_date)

    if key_indicators_data:
        print("\nData retrieved from FRED:")
        display_data(key_indicators_data)

