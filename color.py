import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


# Sample data: RGB values and their corresponding ratings
data = [
    

]
# Create a DataFrame from the data
df = pd.DataFrame(data, columns=['R', 'G', 'B', 'Rating'])

# Group the data by RGB values and calculate the average rating for each unique color
grouped = df.groupby(['R', 'G', 'B']).agg({'Rating': 'mean'}).reset_index()
grouped['Color'] = grouped.apply(
    lambda row: f'rgb({row.R}, {row.G}, {row.B})', axis=1
)

fig = px.scatter_3d(
    grouped,
    x='R',
    y='G',
    z='B',
    size='Rating',
)

fig.update_traces(marker=dict(color=grouped['Color'], opacity=0.8))

fig.update_layout(
    scene=dict(
        xaxis_title='Red',
        yaxis_title='Green',
        zaxis_title='Blue',
        xaxis=dict(range=[0, 255]),
        yaxis=dict(range=[0, 255]),
        zaxis=dict(range=[0, 255])
    )
)

fig.show()

