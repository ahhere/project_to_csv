# README

## Overview
This script interacts with the BrainTrust API to fetch both metadata and data content from datasets and experiments. For each dataset, it retrieves both the dataset metadata and its actual data content using BTQL queries. For experiments, it retrieves the experiment metadata. All results are organized in a clear directory structure and saved as CSV files.


### Network Diagnostics
The script includes automatic network diagnostics capabilities:

1. **Automatic Traceroute**:
   - If an API request times out or fails
   - If there are connectivity issues
   - The script will automatically run a traceroute to the API endpoint

2. **Timeout Handling**:
   - API requests timeout after 10 seconds
   - Upon timeout, network diagnostics are automatically triggered
   - Results are displayed in the console

Example traceroute output:
```bash
API request error: HTTPSConnectionPool(host='api.braintrust.dev', port=443): Read timed out
Running traceroute for api.braintrust.dev...
traceroute to api.braintrust.dev (123.45.67.89), 30 hops max, 60 byte packets
 1  router.local  (192.168.1.1)  1.123 ms  1.234 ms  1.345 ms
 2  isp-gateway  (10.0.0.1)  12.345 ms  12.456 ms  12.567 ms
...

---

## Prerequisites
### 1. Python
Ensure you have Python 3.8 or newer installed on your system. You can check your Python version with the following command:

```bash
python --version
```
or
```bash
python3 --version
```

### 2. Virtual Environment
It is recommended that you run this script in a virtual environment and install the dependencies in requirements.txt inside that environment.
---

## Setting Up the Environment
### 1. Activate the Virtual Environment
Activate the provided virtual environment:

#### On Linux/MacOS:
```bash
source my-venv/bin/activate
```

#### On Windows (Command Prompt):
```cmd
my-venv\Scripts\activate
```

#### On Windows (PowerShell):
```powershell
.\my-venv\Scripts\Activate.ps1
```

### 2. Install Dependencies (if needed)
If dependencies are missing, you can install them using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## Setting Up the API Key
The script requires an API key to authenticate with the BrainTrust API. Set the API key as an environment variable named `BRAINTRUST_API_KEY`.

### Linux/MacOS
Add the following line to your `.bashrc`, `.zshrc`, or terminal session:

```bash
export BRAINTRUST_API_KEY="your_api_key_here"
```

### Windows (Command Prompt)
```cmd
set BRAINTRUST_API_KEY=your_api_key_here
```

### Windows (PowerShell)
```powershell
$env:BRAINTRUST_API_KEY="your_api_key_here"
```

Replace `your_api_key_here` with your actual API key.

---

## How to Run the Script
1. Activate the virtual environment as described above.
2. Ensure the `BRAINTRUST_API_KEY` environment variable is set.
3. Run the script by entering the following command in the terminal:

```bash
python script.py
```

4. When prompted, enter the **Project ID** for which you want to fetch datasets and experiments.

Example:

```text
Enter the project ID: 5464d38b-037d-4714-aedc-6ccd18bd27b5
```

5. The script will create an organized directory structure and save all files within it.

---

## Output
The script creates an organized directory structure for all exported files:

```
exports/
└── project_id/
    ├── datasets/
    │   ├── dataset1_metadata.csv  # Dataset configuration and metadata
    │   ├── dataset1_data.csv      # Actual dataset contents
    │   ├── dataset2_metadata.csv
    │   └── dataset2_data.csv
    └── experiments/
        ├── experiment1.csv        # Experiment metadata
        └── experiment2.csv
```

For each dataset, two files are created:
- `dataset_name_metadata.csv`: Contains dataset configuration and metadata
- `dataset_name_data.csv`: Contains the actual dataset records

For each experiment:
- `experiment_name.csv`: Contains experiment metadata

All spaces and special characters in names are replaced with underscores (`_`) for file compatibility.

---

## Troubleshooting
### Common Issues
1. **API Key Not Found**:
   - Ensure the `BRAINTRUST_API_KEY` environment variable is correctly set and exported.
   - Verify the key by running:
     ```bash
     echo $BRAINTRUST_API_KEY  # Linux/MacOS
     echo %BRAINTRUST_API_KEY%  # Windows Command Prompt
     $env:BRAINTRUST_API_KEY  # Windows PowerShell
     ```

2. **Dependencies Missing**:
   - Ensure you have activated the virtual environment before running the script.
   - Reinstall dependencies with:
     ```bash
     pip install -r requirements.txt
     ```

3. **Permission Denied**:
   - Check your file permissions in the export directory.

4. **BTQL Query Errors**:
   - If you encounter errors with dataset data retrieval, check that:
     - The dataset contains data
     - Your API key has appropriate permissions
     - The dataset ID is valid

### Data Processing Notes
- Large datasets are retrieved in batches of 100 records
- The script handles pagination automatically
- All JSON and list fields are properly escaped in the CSV output
