import random
import json
import os
import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import gspread
from google.oauth2.service_account import Credentials

# Load colors data from JSON
with open("colors_data.json", "r") as f:
    data = json.load(f)

color_cells = data["color_cells"]
id_cells = data["id_cells"]
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Use local credentials.json if it exists, otherwise use Streamlit secrets
if os.path.exists("credentials.json"):
    with open("credentials.json", "r") as f:
        service_account_info = json.load(f)
elif "gcp_service_account" in st.secrets:
    service_account_info = st.secrets["gcp_service_account"]
else:
    st.error("Google Sheets credentials not configured. Please add credentials.json locally or configure secrets in Streamlit Cloud.")
    st.stop()

creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Color Ratings").sheet1
    
