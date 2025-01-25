# README

## Overview
This script is designed to interact with the BrainTrust API. It fetches datasets and experiments for a specific project and saves each result into its own CSV file.

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
This project includes a virtual environment named `my-venv` with all the necessary dependencies pre-installed.

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

5. After execution, CSV files for the datasets and experiments will be saved in the same directory as the script.

---

## Output
Each dataset and experiment will be saved to its own CSV file, named based on its `name` field. Spaces in names will be replaced with underscores (`_`).

Example file names:
- `Prompt_A_(gpt-4o)_dataset.csv`
- `Prompt_B_(gpt-4o)_experiment.csv`

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
   - Check your file permissions in the directory where the script is run.

### Debugging Network Errors
If the script encounters a timeout or network issue, it will attempt to run a traceroute to diagnose connectivity issues.


