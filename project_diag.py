import requests
import csv
import os
import subprocess
import json

def fetch_api_data(api_url, headers=None, params=None):
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Request to {api_url} timed out.")
        run_traceroute(api_url)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        run_traceroute(api_url)
    return None

def run_traceroute(api_url):
    print(f"Running traceroute for {api_url}...")
    try:
        host = api_url.split("//")[-1].split("/")[0]
        result = subprocess.run(["traceroute", host], capture_output=True, text=True, check=True)
        print("Traceroute results:\n", result.stdout)
    except FileNotFoundError:
        print("Traceroute command is not available on this system.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running traceroute: {e}")
    except Exception as e:
        print(f"Unexpected error during traceroute: {e}")

def write_to_csv(data, output_file):
    try:
        if not data or not isinstance(data, list):
            print(f"Warning: No valid data found for {output_file}.")
            return

        headers = set()
        for row in data:
            headers.update(row.keys())

        if not headers:
            print(f"Warning: No valid headers found for {output_file}.")
            return

        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(headers))
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Successfully wrote {len(data)} rows to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to {output_file}: {e}")

def extract_fields(obj, relevant_fields):
    data = {}
    for field in relevant_fields:
        value = obj.get(field)
        if value is not None:
            data[field] = json.dumps(value) if isinstance(value, (dict, list)) else value
    return data

if __name__ == "__main__":
    BASE_URL = "https://api.braintrust.dev/v1"
    API_KEY = os.getenv("BRAINTRUST_API_KEY")
    if not API_KEY:
        print("API key not found. Please set the 'BRAINTRUST_API_KEY' environment variable.")
        exit(1)

    HEADERS = {"Authorization": f"Bearer {API_KEY}"}
    PROJECT_ID = input("Enter the project ID: ").strip()

    os.makedirs("datasets", exist_ok=True)
    os.makedirs("experiments", exist_ok=True)

    # Fetch datasets
    DATASETS_URL = f"{BASE_URL}/dataset"
    datasets_response = fetch_api_data(DATASETS_URL, headers=HEADERS, params={"project_id": PROJECT_ID})
    if datasets_response:
        datasets = datasets_response.get("objects", [])
        print(f"Found {len(datasets)} datasets")
        for dataset in datasets:
            dataset_name = dataset.get("name", "unknown_dataset").replace(" ", "_")
            dataset_data = extract_fields(dataset, dataset.keys())
            output_file = os.path.join("datasets", f"{dataset_name}_dataset.csv")
            write_to_csv([dataset_data], output_file)
    
    # Fetch experiments
    EXPERIMENTS_URL = f"{BASE_URL}/experiment"
    experiments_response = fetch_api_data(EXPERIMENTS_URL, headers=HEADERS, params={"project_id": PROJECT_ID})
    if experiments_response:
        experiments = experiments_response.get("objects", [])
        print(f"Found {len(experiments)} experiments")
        for experiment in experiments:
            experiment_name = experiment.get("name", "unknown_experiment").replace(" ", "_")
            experiment_data = extract_fields(experiment, experiment.keys())
            output_file = os.path.join("experiments", f"{experiment_name}_experiment.csv")
            write_to_csv([experiment_data], output_file)
