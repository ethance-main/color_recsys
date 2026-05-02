import random
import json
import os
import streamlit as st
from streamlit_star_rating import st_star_rating
import recsys

# Load color metadata from JSON
with open("colors_data.json", "r") as f:
    data = json.load(f)

color_cells = data["color_cells"]
id_cells = data["id_cells"]

st.title("Color Recommendation System")

try:
    all_ratings = recsys.load_ratings("responses.csv")
except FileNotFoundError:
    st.error("Could not find responses.csv. Please generate it by syncing Google Sheets or placing a local copy in the app folder.")
    st.stop()
except Exception as exc:
    st.error(f"Failed to load rating data: {exc}")
    st.stop()

if "sample" not in st.session_state:
    st.session_state.sample = random.sample(list(zip(id_cells, color_cells)), 3)

sample = st.session_state.sample

with st.form("color_ratings"):
    st.markdown("### Rate these 3 colors")
    st.markdown(
        "Rate each color on a scale from 1 to 10. After submitting, you will see the top recommended colors based on ratings from similar users."
    )

    responses = []
    for i, (color_id, color_str) in enumerate(sample, start=1):
        rgb = tuple(int(value.strip()) for value in color_str.strip("[]").split(","))
        color_box = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

        st.markdown(
            f"<div style='display:flex;justify-content:center;align-items:center;'>"
            f"<div style='width:150px;height:150px;background-color:{color_box};border-radius:12px;border:2px solid #333;'></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        rating = st_star_rating(
            f"Rate Color {i}",
            maxValue=10,
            defaultValue=5,
            key=f"rating_{color_id}",
        )
        responses.append((color_id, rating))

    submitted = st.form_submit_button("Submit Ratings")

if submitted:
    user_vector = recsys.build_user_vector(responses, n_items=len(color_cells))
    recommendations = recsys.recommend_colors(user_vector, all_ratings, top_n=5, top_k=5)

    st.success("Thank you! Here are your top recommended colors:")

    if not recommendations:
        st.warning("No recommendations could be generated from the available ratings data.")
    else:
        for rank, (color_id, score) in enumerate(recommendations, start=1):
            color_str = color_cells[color_id]
            rgb = tuple(int(value.strip()) for value in color_str.strip("[]").split(","))
            color_box = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

            st.markdown(
                f"<div style='display:flex;align-items:center;margin-bottom:16px;'>"
                f"<div style='width:120px;height:120px;background-color:{color_box};border-radius:12px;border:2px solid #333;margin-right:16px;'></div>"
                f"<div><strong>Recommendation {rank}</strong><br>Color ID: {color_id}<br>Predicted score: {score:.2f}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        "---\n" \
        "This recommendation uses cosine similarity between your ratings and existing \
" \
        "responses from other users in `responses.csv`. The system predicts unrated colors by \
" \
        "combining similar users' ratings."
    )
