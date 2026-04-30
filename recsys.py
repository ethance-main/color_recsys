import gsheets
import pandas as pd

def main():
    # Pull data from Google Sheets and save to local CSV file
    gsheets.gsheets_pull()
    # Load CSV file into a DataFrame
    df = pd.read_csv("responses.csv")

def cosine_similarity(vecA, vecB):
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vecA, vecB))
    magnitudeA = sum(a ** 2 for a in vecA) ** 0.5
    magnitudeB = sum(b ** 2 for b in vecB) ** 0.5
    if magnitudeA == 0 or magnitudeB == 0:
        return 0.0
    return dot_product / (magnitudeA * magnitudeB)

def recommend_colors(user_ratings, all_ratings, top_n=5):
    """Recommend colors based on user ratings and all ratings."""
    similarities = []
    for idx, ratings in all_ratings.iterrows():
        sim = cosine_similarity(user_ratings, ratings)
        similarities.append((idx, sim))
    # Sort by similarity and return top N recommendations
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]



if __name__ == "__main__":
    main()