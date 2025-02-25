# README

## Overview
This script (`project_diag.py`) interacts with the BrainTrust API to export complete project data. It fetches both datasets and experiments for a project, retrieves all associated data using BTQL queries, and saves everything into organized CSV files with metadata headers.

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
python project_diag.py
```

4. When prompted, enter the **Project ID** for which you want to fetch data.

Example:

```text
Enter the project ID: 5464d38b-037d-4714-aedc-6ccd18bd27b5
```

5. The script will create a directory structure and save all files within it.

---

## Output
The script creates an organized directory structure for all exported files:

```
exports/
└── project_id/
    ├── datasets/
    │   ├── Dataset_1.csv      # Contains dataset metadata and all data
    │   └── Dataset_2.csv
    └── experiments/
        ├── Experiment_1.csv   # Contains experiment metadata and all logs/records
        └── Experiment_2.csv
```

For each dataset and experiment, a single comprehensive CSV file is created containing:
- A metadata section with key information (ID, name, project_id, etc.)
- The actual data with all fields preserved

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

### Network Diagnostics
If the script encounters a timeout or network issue, it will automatically run a traceroute to diagnose connectivity issues. This helps identify:
- Network connectivity problems
- DNS resolution issues
- Routing problems

The traceroute results will be displayed in the console to help diagnose any API connectivity issues.

---

## Features
1. **Complete Data Export**: 
   - Retrieves all datasets, experiments, and their associated data
   - Preserves all original fields and values

2. **Metadata Headers**:
   - Each CSV includes relevant metadata as header rows
   - Clear separation between metadata and data

3. **Organized Structure**:
   - Clean directory organization
   - Consistent file naming

4. **Network Diagnostics**:
   - Automatic traceroute for connection issues
   - Detailed error reporting
