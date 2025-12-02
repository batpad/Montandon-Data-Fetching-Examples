# Montandon Data Fetching Examples

Example notebooks demonstrating usage of the Montandon API / STAC data catalog.

## Run in Binder

Click to open the notebooks in an interactive environment:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/arunissun/Montandon-Data-Fetching-Examples/HEAD)

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
- `06_Snow_Cold_Wave_Impact_Analysis.ipynb` - Winter hazard impact analysis
- `07_cascading_impacts_analysis.ipynb` - 2023 Turkey-Syria earthquake cascading impacts
