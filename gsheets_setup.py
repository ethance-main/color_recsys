import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import itertools
import json
import gspread
from google.oauth2.service_account import Credentials
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load credentials from local JSON file
with open('credentials.json', 'r') as f:
    service_account_info = json.load(f)

creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Color Ratings").sheet1
levels = [0, 64, 128, 192, 255]
colors = list(itertools.product(levels, levels, levels))

# Build rows: all colors in one row, all color IDs in the next row
color_cells = [f"[{r},{g},{b}]" for r, g, b in colors]
id_cells = list(range(125))

# First row: all colors as [r,g,b] strings
sheet.append_row(color_cells)
# Second row: all color IDs
sheet.append_row(id_cells)

# Save to JSON for use in other scripts
import json
data = {"color_cells": color_cells, "id_cells": id_cells}
with open("colors_data.json", "w") as f:
    json.dump(data, f)