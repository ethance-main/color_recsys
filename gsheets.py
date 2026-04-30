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

# REQUIRES: credentials.json with appropriate permissions to access Google Sheets API
# MODIFIES: Google Sheet "Color Ratings" by adding two rows - one with all 125 colors
#  as [r,g,b] strings, and one with all color IDs (0-124)
# EFFECTS: Initializes the Google Sheet with all colors and their corresponding IDs,
#  and saves the same data to a local JSON file for use in the Streamlit app. 
#  Only needs to be run once to set up the sheet.
def initialize_gsheet(title="Color Ratings"):
    with open('credentials.json', 'r') as f:
        service_account_info = json.load(f)
    # Establishing credentials and client connection to Google Sheets API
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(title).sheet1
    # Generating combinations of RGB values at 5 levels to create a palette of 125 colors
    levels = [0, 64, 128, 192, 255]
    colors = list(itertools.product(levels, levels, levels))
    color_cells = [f"[{r},{g},{b}]" for r, g, b in colors]
    id_cells = list(range(125))
    # First row: all colors as [r,g,b] strings
    sheet.append_row(color_cells)
    # Second row: all color IDs
    sheet.append_row(id_cells)
    # Save same data to local JSON file for consistent color-id pairs
    data = {"color_cells": color_cells, "id_cells": id_cells}
    with open("colors_data.json", "w") as f:
        json.dump(data, f)


def recompute_color_data_json():
    # This function can be used to recompute the color data if needed
    levels = [0, 64, 128, 192, 255]
    colors = list(itertools.product(levels, levels, levels))
    color_cells = [f"[{r},{g},{b}]" for r, g, b in colors]
    id_cells = list(range(125))
    data = {"color_cells": color_cells, "id_cells": id_cells}
    with open("colors_data.json", "w") as f:
        json.dump(data, f)

# REQUIRES: Google Sheet initialized with initialize_gsheet() function, 
#   and credentials.json with appropriate permissions
# MODIFIES: responses.csv file in local directory with all user responses from the Google Sheet
# EFFECTS: Pulls color data (color_cells and id_cells) from the Google Sheet and returns as two lists
def gsheets_pull(title="Color Ratings"):
    with open('credentials.json', 'r') as f:
        service_account_info = json.load(f)
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(title).sheet1
    # Pull all data from the sheet
    data = sheet.get_all_values()
    # extract data as csv file, remove first two rows (headers), remove leftmost column (userID)
    with open("responses.csv", "w") as f:
        for row in data[2:]:
            f.write(",".join(row[1:]) + "\n")
    
    