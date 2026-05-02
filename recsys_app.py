import random
import json
import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import recsys

# Load colors data from JSON
with open("colors_data.json", "r") as f:
    data = json.load(f)

color_cells = data["color_cells"]
id_cells = data["id_cells"]


def load_all_ratings():
    try:
        return recsys.load_ratings("responses.csv")
    except FileNotFoundError:
        return pd.DataFrame()


st.title("Color Recommendation System")
color_data = list(zip(id_cells, color_cells))
if "sample" not in st.session_state:
    st.session_state.sample = random.sample(color_data, 3)
sample = st.session_state.sample

with st.form("color_ratings"):
    st.markdown("### Instructions")
    st.markdown(
        "Please rate the 3 colors below on a scale of 1-10 stars (1 star = not appealing, 10 stars = very appealing). "
        "After submitting, your choices will be compared with our predicted ratings from similar users."
    )
    responses = []
    for i, (color_id, color_str) in enumerate(sample):
        rgb = color_str.strip("[]").split(",")
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        color_box = f"rgb({r},{g},{b})"

        st.markdown(
            f"<div style='display:flex;justify-content:center;align-items:center;'>"
            f"<div style='width:150px;height:150px;background-color:{color_box};border-radius:10px;border:2px solid #333;'></div>"
            f"</div>",
            unsafe_allow_html=True
        )
        rating = st_star_rating(f"Rate Color {i+1}", maxValue=10, defaultValue=5, key=f"rating_{color_id}")
        responses.append((color_id, rating))

    submitted = st.form_submit_button("Submit Ratings")

if submitted:
    all_ratings = load_all_ratings()
    recommendations = recsys.recommend_colors(responses, all_ratings, top_n=5, top_k=5)

    if recommendations:
        st.markdown("### Recommended colors for you")
        for rank, (color_id, score) in enumerate(recommendations, start=1):
            color_str = color_cells[color_id]
            r, g, b = [int(value.strip()) for value in color_str.strip("[]").split(",")]
            color_box = f"rgb({r},{g},{b})"
            st.markdown(
                f"<div style='display:flex;align-items:center;margin-bottom:16px;'>"
                f"<div style='width:120px;height:120px;background-color:{color_box};border-radius:10px;border:2px solid #333;margin-right:16px;'></div>"
                f"<div><strong>{rank}. Color ID {color_id}</strong><br>Predicted score: {score:.2f}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.warning("No historical ratings are available yet to generate recommendations.")
