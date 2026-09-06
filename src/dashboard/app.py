"""
NAOMI Executive Decision Dashboard Application.

Entry point for launching the Plotly Dash C-suite Decision Companion interface.
Run locally via:
    python src/dashboard/app.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import dash
import dash_bootstrap_components as dbc

from src.dashboard.layouts.main_layout import build_main_layout
from src.dashboard.callbacks.main_callbacks import register_callbacks

# Path to custom CSS assets
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# Initialize Dash application with Bootstrap Darkly and Bootstrap Icons
app = dash.Dash(
    __name__,
    title="NAOMI | AI Business Decision Companion",
    assets_folder=str(ASSETS_DIR),
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Underlying Flask WSGI server
server = app.server

# Set layout tree
app.layout = build_main_layout()

# Register reactive analytical callbacks
register_callbacks(app)


if __name__ == "__main__":
    print("=" * 80)
    print("NAOMI: LAUNCHING EXECUTIVE DECISION DASHBOARD")
    print("Access the dashboard live in your browser at: http://127.0.0.1:8050")
    print("=" * 80)
    app.run(host="0.0.0.0", port=8050, debug=False)
