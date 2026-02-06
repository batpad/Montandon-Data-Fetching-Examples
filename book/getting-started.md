# Getting Started

This guide will help you set up your environment to run the Montandon data fetching examples locally.

## Prerequisites

Before you begin, ensure you have:

- Python 3.9 or higher
- Git (for cloning the repository)
- A modern web browser
- An IFRC account for API access

## Step 1: Obtain an API Token

:::{important}
The Montandon STAC API requires authentication. You'll need a valid API token to fetch live data.
:::

### How to Get Your Token

1. **Visit the Authentication Portal**
   - Navigate to [https://goadmin-stage.ifrc.org/](https://goadmin-stage.ifrc.org/)
   - Click "Sign In" and use your IFRC credentials

2. **Generate an API Token**
   - Once logged in, go to your account settings
   - Find the "API Tokens" or "Developer" section
   - Click "Generate New Token"
   - Give your token a descriptive name (e.g., "Montandon Examples")
   - Copy the token immediately - you won't be able to see it again!

3. **Store Your Token Securely**
   
   :::{warning}
   Never commit your API token to version control or share it publicly!
   :::

## Step 2: Set Up Your Environment

### Clone the Repository

```bash
git clone https://github.com/IFRCGo/Montandon-Data-Fetching-Examples.git
cd Montandon-Data-Fetching-Examples
```

### Install Dependencies with uv

This project uses `uv` for dependency management:

```bash
# Install uv if you haven't already
pip install uv

# Install all dependencies
uv sync
```

### Set Your API Token

::::{tab-set}
:::{tab-item} macOS/Linux
```bash
export MONTANDON_API_TOKEN='your_token_here'
```

To make this permanent, add it to your shell profile:
```bash
echo "export MONTANDON_API_TOKEN='your_token_here'" >> ~/.bashrc
# or for zsh users:
echo "export MONTANDON_API_TOKEN='your_token_here'" >> ~/.zshrc
```
:::

:::{tab-item} Windows (PowerShell)
```powershell
$env:MONTANDON_API_TOKEN = "your_token_here"
```

To make this permanent:
```powershell
[System.Environment]::SetEnvironmentVariable('MONTANDON_API_TOKEN', 'your_token_here', 'User')
```
:::

:::{tab-item} Windows (Command Prompt)
```cmd
set MONTANDON_API_TOKEN=your_token_here
```

To make this permanent:
```cmd
setx MONTANDON_API_TOKEN "your_token_here"
```
:::
::::

## Step 3: Launch Jupyter

Start JupyterLab to work with the notebooks:

```bash
uv run jupyter lab
```

This will open JupyterLab in your default browser. Navigate to the `montandon_notebooks/` directory to see all available examples.

## Step 4: Test Your Setup

Open the first notebook (`01_Getting_Started_Montandon_STAC_API.ipynb`) and run the initial cells to verify:

1. ✅ All libraries import successfully
2. ✅ Your API token is detected
3. ✅ You can connect to the Montandon API
4. ✅ You can retrieve sample data

## Working with Pre-executed Notebooks

This JupyterBook displays notebooks with cached outputs. This means:

- ✅ You can see results without running code
- ✅ No API token needed for viewing
- ⚠️ Data shown may not be current
- ⚠️ To get live data, run notebooks locally

## Troubleshooting

### Common Issues and Solutions

:::{dropdown} ImportError: No module named 'pystac_client'
Install the required packages:
```bash
uv sync
```
:::

:::{dropdown} Authentication Error: 401 Unauthorized
Your API token may be:
- Missing: Check if `MONTANDON_API_TOKEN` is set
- Invalid: Verify the token at [goadmin-stage.ifrc.org](https://goadmin-stage.ifrc.org/)
- Expired: Generate a new token
:::

:::{dropdown} Folium maps not displaying
For Jupyter notebooks:
- Ensure JavaScript is enabled
- Try: `jupyter nbextension enable --py folium`
- Consider saving maps as HTML and opening separately
:::

## Next Steps

Now that you're set up:

1. Start with [Introduction to Montandon STAC API](notebooks/01_Getting_Started_Montandon_STAC_API)
2. Explore different data sources and collections
3. Try modifying queries to find specific events
4. Create your own analyses and visualizations

Happy exploring! 🚀