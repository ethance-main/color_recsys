import itertools
import random
import streamlit as st
import pandas as pd

levels = [0, 64, 128, 192, 255]
colors = list(itertools.product(levels, levels, levels))

sample = random.sample(colors, 25)
st.title("Color Ratings")
responses = []

for i, (r, g, b) in enumerate(sample):
    color_box = f"rgb({r},{g},{b})"
    
    st.markdown(
        f"<div style='width:100px;height:100px;background-color:{color_box}'></div>",
        unsafe_allow_html=True
    )
    
    rating = st.slider(f"Color {i+1}", 1, 10)
    
    responses.append((r, g, b, rating))


df = pd.DataFrame(responses, columns=['R','G','B','rating'])
df.to_csv("responses.csv", mode='a', header=False, index=False)