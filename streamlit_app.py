import random
import json
import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import gspread
from google.oauth2.service_account import Credentials
#testing
# Load colors data from JSON
with open("colors_data.json", "r") as f:
    data = json.load(f)

color_cells = data["color_cells"]
id_cells = data["id_cells"]
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open("Color Ratings").sheet1
    

st.title("Color Ratings")

# Create list of (color_id, color_string) tuples
color_data = list(zip(id_cells, color_cells))

if "sample" not in st.session_state:
    st.session_state.sample = random.sample(color_data, 25)
sample = st.session_state.sample

with st.form("color_quiz"):
    responses = []
    for i, (color_id, color_str) in enumerate(sample):
        # Parse for display
        rgb = color_str.strip("[]").split(",")
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        color_box = f"rgb({r},{g},{b})"
    
        st.markdown(
            f"<div style='width:100px;height:100px;background-color:{color_box}'></div>",
            unsafe_allow_html=True
        )
        stars = st_star_rating(f"Rating for Color {i+1}", max_stars=10, defaultValue=5, key=f"rating_{color_id}")
        # Keep color_id with rating as key-value pair
        responses.append((color_id, stars))
    submitted = st.form_submit_button("Submit Ratings")

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
    
    st.success("Ratings submitted successfully!")
    
    # Reset the sample to generate new random colors for next submission
    del st.session_state["sample"]
    st.rerun()