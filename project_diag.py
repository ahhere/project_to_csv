import requests
import csv
import os
import subprocess

# Function to call the API
def fetch_api_data(api_url, headers=None, params=None):
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)  # Set timeout in seconds
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Parse JSON response
    except requests.exceptions.Timeout:
        print(f"Request to {api_url} timed out.")
        run_traceroute(api_url)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        run_traceroute(api_url)
    return None

# Function to run traceroute and output results if a network request fails
def run_traceroute(api_url):
    print(f"Running traceroute for {api_url}...")
    try:
        # Extract host from URL
        host = api_url.split("//")[-1].split("/")[0]
        result = subprocess.run(["traceroute", host], capture_output=True, text=True, check=True)
        print("Traceroute results:\n", result.stdout)
    except FileNotFoundError:
        print("Traceroute command is not available on this system.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running traceroute: {e}")
    except Exception as e:
        print(f"Unexpected error during traceroute: {e}")

# Function to write data to a CSV file
def write_to_csv(data, output_file):
    try:
        # Flatten nested dictionaries
        flattened_data = [flatten_dict(item) for item in data]
        # Extract headers from the first row of the flattened data
        headers = flattened_data[0].keys() if flattened_data else []
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(flattened_data)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to {output_file}: {e}")

# Function to flatten nested dictionaries
def flatten_dict(data):
    flat_data = data.copy()
    metadata = flat_data.pop("metadata", {})
    for key, value in metadata.items():
        flat_data[f"metadata_{key}"] = value
    return flat_data

# Main script
if __name__ == "__main__":
    # Base URLs for the BrainTrust API
    BASE_URL = "https://api.braintrust.dev/v1"

    # Get API key from environment variable
    API_KEY = os.getenv("BRAINTRUST_API_KEY")
    if not API_KEY:
        print("API key not found. Please set the 'BRAINTRUST_API_KEY' environment variable.")
        exit(1)

    # Headers for API requests
    HEADERS = {"Authorization": f"Bearer {API_KEY}"}

    # Replace this with the project ID you want to fetch data for
    PROJECT_ID = input("Enter the project ID: ").strip()

    # Fetch datasets for the given project
    DATASETS_URL = f"{BASE_URL}/dataset"
    datasets_response = fetch_api_data(DATASETS_URL, headers=HEADERS, params={"project_id": PROJECT_ID})

    if datasets_response:
        datasets = datasets_response.get("objects", [])
        for dataset in datasets:
            dataset_name = dataset.get("name", "unknown_dataset").replace(" ", "_")
            output_file = f"{dataset_name}_dataset.csv"
            write_to_csv([dataset], output_file)  # Write each dataset to its own CSV
    else:
        print("No datasets found for the specified project.")

    # Fetch experiments for the given project
    EXPERIMENTS_URL = f"{BASE_URL}/experiment"
    experiments_response = fetch_api_data(EXPERIMENTS_URL, headers=HEADERS, params={"project_id": PROJECT_ID})

    if experiments_response:
        experiments = experiments_response.get("objects", [])
        for experiment in experiments:
            experiment_name = experiment.get("name", "unknown_experiment").replace(" ", "_")
            output_file = f"{experiment_name}_experiment.csv"
            write_to_csv([experiment], output_file)  # Write each experiment to its own CSV
    else:
        print("No experiments found for the specified project.")
