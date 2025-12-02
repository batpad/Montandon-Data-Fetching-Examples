# Montandon Data Fetching Examples

Example notebooks demonstrating usage of the Montandon API / STAC data catalog.

## Authentication Required

The Montandon STAC API staging environment now requires authentication using a Bearer Token from the IFRC OpenID Connect system.

**API Endpoint:** https://montandon-eoapi-stage.ifrc.org/

**To get your API token:**
1. Visit: https://goadmin-stage.ifrc.org/
2. Log in with your IFRC credentials
3. Navigate to your account settings to generate an API token
4. When running notebooks, you'll be prompted to enter your token securely

**Setting token as environment variable (optional):**
```bash
# PowerShell
$env:MONTANDON_API_TOKEN = "your_token_here"

# Bash/Linux
export MONTANDON_API_TOKEN="your_token_here"
```

## Run in Binder

Click to open the notebooks in an interactive environment:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/arunissun/Montandon-Data-Fetching-Examples/HEAD)

**Note:** When using Binder, you'll need to provide your own API token when prompted in the notebooks.

## Run Locally

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/batpad/Montandon-Data-Fetching-Examples.git
cd Montandon-Data-Fetching-Examples

# Install dependencies and run JupyterLab
uv sync
uv run jupyter lab
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/batpad/Montandon-Data-Fetching-Examples.git
cd Montandon-Data-Fetching-Examples

# Create a virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run JupyterLab
jupyter lab
```

## Notebooks

- `01_Getting_Started_Montandon_STAC_API.ipynb` - Introduction to the Montandon STAC API
- `02_Montandon_data_analysis.ipynb` - Data analysis and visualization
- `03_Time_Series_Analysis.ipynb` - Time series analysis of disaster data
- `04_Recent_Cyclone_Tracking.ipynb` - Tracking Hurricane Beryl
- `05_Earthquakes_visualization.ipynb` - Earthquake event visualization
- `06_Hazard_Country_Codes_Analysis.ipynb` - Hazard and country code analysis
- `07_Snow_Cold_Wave_Impact_Analysis.ipynb` - Winter hazard impact analysis
- `08_Queryables_Deep_Dive.ipynb` - Deep dive into STAC API queryables and CQL2 filtering
