import requests
import csv
import os
import json

def fetch_api_data(url, method="GET", headers=None, params=None, body=None):
    """Fetch data from the Braintrust API with error handling."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:  # POST request
            response = requests.post(url, headers=headers, json=body, timeout=10)
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response preview: {response.text[:200]}...")
        
        response.raise_for_status()
        
        # For BTQL endpoint, handle JSONL format
        if url.endswith('/btql'):
            data = []
            for line in response.text.strip().split('\n'):
                if line:  # Skip empty lines
                    data.append(json.loads(line))
            return {"data": data}
        else:
            return response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
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
            break
        
        rows = response.get("data", [])
        if rows:
            all_rows.extend(rows)
            total_fetched += len(rows)
            print(f"Fetched {len(rows)} rows for dataset '{dataset_name}' (Total: {total_fetched})")
            
            if len(rows) < per_request_limit:
                break  # No more data to fetch
        else:
            break  # No data returned
        
        # Get the last record's ID for pagination
        if rows:
            cursor = rows[-1].get("id")
    
    return all_rows

def write_to_csv(data, output_file):
    """Write rows to a CSV file."""
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
                
                # Save dataset metadata
                dataset_data = extract_fields(dataset, dataset.keys())
                metadata_file = os.path.join(datasets_dir, f"{sanitize_filename(dataset_name)}_metadata.csv")
                write_to_csv([dataset_data], metadata_file)
                
                # Fetch and save dataset contents
                rows = fetch_dataset_rows(BASE_URL, HEADERS, dataset_id, dataset_name)
                if rows:
                    data_file = os.path.join(datasets_dir, f"{sanitize_filename(dataset_name)}_data.csv")
                    write_to_csv(rows, data_file)
                else:
                    print(f"No data found for dataset '{dataset_name}'")
    
    # Process Experiments
    print(f"\nFetching experiments for project '{PROJECT_ID}'...")
    experiments = fetch_project_experiments(BASE_URL, HEADERS, PROJECT_ID)
    
    if experiments:
        print(f"Found {len(experiments)} experiments")
        for experiment in experiments:
            experiment_name = experiment.get("name", "unknown_experiment")
            print(f"\nProcessing experiment '{experiment_name}'...")
            
            # Save experiment metadata
            experiment_data = extract_fields(experiment, experiment.keys())
            output_file = os.path.join(experiments_dir, f"{sanitize_filename(experiment_name)}.csv")
            write_to_csv([experiment_data], output_file)
    
    print(f"\nExport complete!")
    print(f"Files are saved in:")
    print(f"- Datasets: {datasets_dir}")
    print(f"- Experiments: {experiments_dir}")
