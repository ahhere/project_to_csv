import requests
import csv
import os
import json
import subprocess

def run_traceroute(api_url):
    """Run network diagnostics using traceroute."""
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

def fetch_api_data(url, method="GET", headers=None, params=None, body=None):
    """Fetch data from the Braintrust API with error handling and network diagnostics."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:  # POST request
            response = requests.post(url, headers=headers, json=body, timeout=10)
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response preview: {response.text[:300]}...")
        
        response.raise_for_status()
        
        # For BTQL endpoint, handle JSONL format
        if url.endswith('/btql'):
            data = []
            for line in response.text.strip().split('\n'):
                if line:  # Skip empty lines
                    try:
                        parsed_line = json.loads(line)
                        data.append(parsed_line)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line: {line}")
                        print(f"Error details: {e}")
            return {"data": data}
        else:
            return response.json()
            
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out.")
        run_traceroute(url)
        return None
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        run_traceroute(url)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response.text}")
        return None

def fetch_project_datasets(base_url, headers, project_id):
    """Retrieve all datasets for a given project ID."""
    url = f"{base_url}/v1/dataset"
    params = {"project_id": project_id}
    response = fetch_api_data(url, headers=headers, params=params)
    
    if response and "objects" in response:
        return response["objects"]
    else:
        print(f"No datasets found in project {project_id}.")
        return []

def fetch_project_experiments(base_url, headers, project_id):
    """Retrieve all experiments for a given project ID."""
    url = f"{base_url}/v1/experiment"
    params = {"project_id": project_id}
    response = fetch_api_data(url, headers=headers, params=params)
    
    if response and "objects" in response:
        return response["objects"]
    else:
        print(f"No experiments found in project {project_id}.")
        return []

def fetch_dataset_rows(base_url, headers, dataset_id, dataset_name, per_request_limit=100):
    """Fetch actual dataset rows using BTQL query with pagination."""
    url = f"{base_url}/btql"
    cursor = None
    all_rows = []
    total_fetched = 0
    
    print(f"Attempting to fetch data for dataset: {dataset_id} ({dataset_name})")
    
    while True:
        btql_query = {
            "from": {
                "op": "function",
                "name": {
                    "op": "ident",
                    "name": ["dataset"]
                },
                "args": [{
                    "op": "literal",
                    "value": dataset_id
                }]
            },
            "select": [{
                "op": "star"
            }],
            "limit": per_request_limit
        }
        
        if cursor:
            btql_query["cursor"] = cursor
            
        body = {
            "query": btql_query,
            "fmt": "jsonl"
        }
        
        print(f"\nSending BTQL query: {json.dumps(body, indent=2)}")
        
        response = fetch_api_data(url, method="POST", headers=headers, body=body)
        
        if not response:
            print("No response received from API for dataset query")
            break
        
        rows = response.get("data", [])
        if rows:
            all_rows.extend(rows)
            total_fetched += len(rows)
            print(f"Fetched {len(rows)} rows for dataset '{dataset_name}' (Total: {total_fetched})")
            
            if len(rows) < per_request_limit:
                break  # No more data to fetch
        else:
            print("Response contained no rows")
            break  # No data returned
        
        # Get the last record's ID for pagination
        if rows:
            cursor = rows[-1].get("id")
            print(f"Next cursor: {cursor}")
    
    return all_rows

def fetch_experiment_logs(base_url, headers, experiment_id, experiment_name, per_request_limit=100):
    """Fetch logs for an experiment using BTQL query with pagination."""
    url = f"{base_url}/btql"
    cursor = None
    all_logs = []
    total_fetched = 0
    
    print(f"Attempting to fetch logs for experiment: {experiment_id} ({experiment_name})")
    
    while True:
        btql_query = {
            "from": {
                "op": "function",
                "name": {
                    "op": "ident",
                    "name": ["experiment"]
                },
                "args": [{
                    "op": "literal",
                    "value": experiment_id
                }]
            },
            "select": [{
                "op": "star"
            }],
            "limit": per_request_limit
        }
        
        if cursor:
            btql_query["cursor"] = cursor
            
        body = {
            "query": btql_query,
            "fmt": "jsonl"
        }
        
        print(f"\nSending BTQL query for experiment logs: {json.dumps(body, indent=2)}")
        
        response = fetch_api_data(url, method="POST", headers=headers, body=body)
        
        if not response:
            print(f"No response received from API for experiment query")
            break
        
        logs = response.get("data", [])
        if logs:
            all_logs.extend(logs)
            total_fetched += len(logs)
            print(f"Fetched {len(logs)} logs for experiment '{experiment_name}' (Total: {total_fetched})")
            
            if len(logs) < per_request_limit:
                break  # No more data to fetch
        else:
            print("Response contained no logs")
            break  # No data returned
        
        # Get the last record's ID for pagination
        if logs:
            cursor = logs[-1].get("id")
            print(f"Next cursor: {cursor}")
    
    return all_logs

def fetch_experiment_records(base_url, headers, experiment_id, experiment_name):
    """Fetch records for an experiment using the record endpoint."""
    url = f"{base_url}/v1/record"
    params = {"experiment_id": experiment_id}
    
    print(f"Fetching records for experiment '{experiment_name}' (ID: {experiment_id})...")
    response = fetch_api_data(url, headers=headers, params=params)
    
    if response and "objects" in response:
        records = response["objects"]
        print(f"Found {len(records)} records for experiment '{experiment_name}'")
        return records
    else:
        print(f"No records found for experiment '{experiment_name}'")
        return []

def write_to_csv_with_metadata(data, metadata, output_file, metadata_fields=None):
    """Write rows to a CSV file with metadata as headers."""
    if not data:
        print(f"No data to write for {output_file}")
        return
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Collect all possible field names from all records
    fieldnames = set()
    for record in data:
        if isinstance(record, dict):
            fieldnames.update(record.keys())
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write metadata as header rows
        writer.writerow(["# METADATA"])
        
        # If specific metadata fields are provided, use only those
        if metadata_fields:
            for field in metadata_fields:
                if field in metadata:
                    value = metadata[field]
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    writer.writerow([f"# {field}", value])
        else:
            # Otherwise use all metadata fields
            for field, value in metadata.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                writer.writerow([f"# {field}", value])
        
        writer.writerow([])  # Empty row to separate metadata from data
        writer.writerow(["# DATA"])
        
        # Write the actual data
        dict_writer = csv.DictWriter(file, fieldnames=sorted(list(fieldnames)))
        dict_writer.writeheader()
        dict_writer.writerows(data)
    
    print(f"Saved {len(data)} rows to {output_file} with metadata headers")

def write_to_csv(data, output_file):
    """Write rows to a CSV file (without metadata)."""
    if not data:
        print(f"No data to write for {output_file}")
        return
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Collect all possible field names from all records
    fieldnames = set()
    for record in data:
        fieldnames.update(record.keys())
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=sorted(list(fieldnames)))
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Saved {len(data)} rows to {output_file}")

def extract_fields(obj, relevant_fields):
    """Extract and format fields from an object."""
    data = {}
    for field in relevant_fields:
        value = obj.get(field)
        if value is not None:
            data[field] = json.dumps(value) if isinstance(value, (dict, list)) else value
    return data

def sanitize_filename(name):
    """Convert a string into a valid filename."""
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)

if __name__ == "__main__":
    BASE_URL = "https://api.braintrust.dev"
    API_KEY = os.getenv("BRAINTRUST_API_KEY")
    
    if not API_KEY:
        print("API key not found. Set the BRAINTRUST_API_KEY environment variable.")
        exit(1)
    
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    PROJECT_ID = input("Enter the project ID: ").strip()
    base_output_dir = "exports"
    project_dir = os.path.join(base_output_dir, sanitize_filename(PROJECT_ID))
    
    # Create directories for datasets and experiments
    datasets_dir = os.path.join(project_dir, "datasets")
    experiments_dir = os.path.join(project_dir, "experiments")
    os.makedirs(datasets_dir, exist_ok=True)
    os.makedirs(experiments_dir, exist_ok=True)
    
    # Process Datasets
    print(f"\nFetching datasets for project '{PROJECT_ID}'...")
    datasets = fetch_project_datasets(BASE_URL, HEADERS, PROJECT_ID)
    
    if datasets:
        print(f"Found {len(datasets)} datasets")
        for dataset in datasets:
            dataset_id = dataset.get("id")
            dataset_name = dataset.get("name", "unknown_dataset")
            
            if dataset_id and dataset_name:
                print(f"\nProcessing dataset '{dataset_name}' (ID: {dataset_id})...")
                
                # Extract dataset metadata
                dataset_metadata = extract_fields(dataset, dataset.keys())
                
                # Important metadata fields to include in data file
                important_metadata = ["id", "name", "project_id", "created", "description"]
                
                # Fetch dataset contents
                rows = fetch_dataset_rows(BASE_URL, HEADERS, dataset_id, dataset_name)
                if rows:
                    # Save dataset contents with metadata headers
                    data_file = os.path.join(datasets_dir, f"{sanitize_filename(dataset_name)}.csv")
                    write_to_csv_with_metadata(rows, dataset_metadata, data_file, important_metadata)
                else:
                    print(f"No data found for dataset '{dataset_name}', saving metadata only")
                    # If no data found, save just the metadata
                    metadata_file = os.path.join(datasets_dir, f"{sanitize_filename(dataset_name)}.csv")
                    write_to_csv([dataset_metadata], metadata_file)
    
    # Process Experiments
    print(f"\nFetching experiments for project '{PROJECT_ID}'...")
    experiments = fetch_project_experiments(BASE_URL, HEADERS, PROJECT_ID)
    
    if experiments:
        print(f"Found {len(experiments)} experiments")
        for experiment in experiments:
            experiment_id = experiment.get("id")
            experiment_name = experiment.get("name", "unknown_experiment")
            
            if experiment_id and experiment_name:
                print(f"\nProcessing experiment '{experiment_name}' (ID: {experiment_id})...")
                
                # Extract experiment metadata
                experiment_metadata = extract_fields(experiment, experiment.keys())
                
                # Important metadata fields to include in logs file
                important_metadata = ["id", "name", "project_id", "dataset_id", "created", "description"]
                
                # Fetch experiment logs using BTQL
                logs = fetch_experiment_logs(BASE_URL, HEADERS, experiment_id, experiment_name)
                if logs:
                    # Save logs with metadata headers directly
                    logs_file = os.path.join(experiments_dir, f"{sanitize_filename(experiment_name)}.csv")
                    write_to_csv_with_metadata(logs, experiment_metadata, logs_file, important_metadata)
                else:
                    print(f"No logs found for experiment '{experiment_name}'")
                    
                    # If no logs found using BTQL, try fetching experiment records directly
                    records = fetch_experiment_records(BASE_URL, HEADERS, experiment_id, experiment_name)
                    if records:
                        # Save records with metadata headers
                        records_file = os.path.join(experiments_dir, f"{sanitize_filename(experiment_name)}.csv")
                        write_to_csv_with_metadata(records, experiment_metadata, records_file, important_metadata)
                    else:
                        # If still no data, save just the experiment metadata
                        print(f"No data found for experiment '{experiment_name}', saving metadata only")
                        metadata_file = os.path.join(experiments_dir, f"{sanitize_filename(experiment_name)}.csv")
                        write_to_csv([experiment_metadata], metadata_file)
    
    print(f"\nExport complete!")
    print(f"Files are saved in:")
    print(f"- Datasets: {datasets_dir}")
    print(f"- Experiments: {experiments_dir}")
