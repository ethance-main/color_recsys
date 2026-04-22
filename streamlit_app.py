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
    

st.title("Color Ratings")

# Create list of (color_id, color_string) tuples
color_data = list(zip(id_cells, color_cells))

if "sample" not in st.session_state:
    st.session_state.sample = random.sample(color_data, 25)
sample = st.session_state.sample

with st.form("color_quiz"):
    st.markdown("### Instructions")
    st.markdown("Rate how much you like each color on a scale of 1-10 stars. Colors are randomly sampled each time you submit, so feel free to submit multiple times to rate more colors!")
    
    # Check if already submitted - if so, skip the form entirely
    if not st.session_state.get("submitted", False):
        responses = []
        for i, (color_id, color_str) in enumerate(sample):
            # Parse for display
            rgb = color_str.strip("[]").split(",")
            r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            color_box = f"rgb({r},{g},{b})"
        
            st.markdown(
                f"<div style='display:flex;justify-content:center;align-items:center;'>"
                f"<div style='width:150px;height:150px;background-color:{color_box};border-radius:10px;border:2px solid #333;'></div>"
                f"</div>",
                unsafe_allow_html=True
            )
            stars = st_star_rating(f"How much do you like Color {i+1}?", maxValue=10, defaultValue=1, key=f"rating_{color_id}")
            # Keep color_id with rating as key-value pair
            responses.append((color_id, stars))
        
        submitted = st.form_submit_button("Submit Ratings")
    else:
        submitted = False

if submitted:
    df = pd.DataFrame(responses, columns=['color_id', 'rating'])
    st.dataframe(df)
    
    # Get the current number of submissions to use as unique ID
    # (subtract 2 to account for the header rows with colors and IDs)
    existing_rows = len(sheet.get_all_values())
    submission_id = max(1, existing_rows - 2)  # Start at 1, increment for each submission
    
    # Create a list of 125 ratings, defaulting to 0 for unrated colors
    ratings_row = [0] * 125
    for color_id, rating in responses:
        ratings_row[color_id] = rating
    
    # Prepend submission_id to the ratings row
    full_row = [submission_id] + ratings_row
    
    # Append the full row to Google Sheets
    sheet.append_row(full_row)
    
    # Mark as submitted to disable button
    st.session_state["submitted"] = True
    
    st.success("Thank you for your ratings!")
    st.markdown("You may close this window now.")