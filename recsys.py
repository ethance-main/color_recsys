import json
import pandas as pd
import gsheets

# REQUIRES: responses.csv
# MODIFIES: None
# EFFECTS: Returns dataframe with all user ratings from the CSV file. Each row is a user, each column is an item, and values are ratings (0 if not rated).
def load_ratings(path="responses.csv"):
    df = pd.read_csv(path, header=None, dtype=float)
    return df

# REQUIRES: colors_data.json
# MODIFIES: None
# EFFECTS: Loads color metadata from the JSON file and returns it as a dictionary.
def load_color_metadata(path="colors_data.json"):
    with open(path, "r") as f:
        return json.load(f)


# REQUIRES: rated_items is a list of (item_id, rating) pairs, n_items is the total number of items
# MODIFIES: None
# EFFECTS: Builds a full-length rating vector from the partial user ratings, filling in 0 for unrated items.
def build_user_vector(rated_items, n_items=125):
    vector = [0.0] * n_items
    for item_id, rating in rated_items:
        if item_id is None:
            continue
        try:
            item_id = int(item_id)
            rating = float(rating)
        except (TypeError, ValueError):
            continue
        if 0 <= item_id < n_items:
            vector[item_id] = rating
    return vector

# REQUIRES: two vectors of the same length
# MODIFIES: None
# EFFECTS: Computes and returns the cosine similarity between the two vectors
def cosine_similarity(vecA, vecB):
    dot_product = sum(a * b for a, b in zip(vecA, vecB))
    magnitudeA = sum(a ** 2 for a in vecA) ** 0.5
    magnitudeB = sum(b ** 2 for b in vecB) ** 0.5
    if magnitudeA == 0 or magnitudeB == 0:
        return 0.0
    return dot_product / (magnitudeA * magnitudeB)

# REQUIRES: user_vector is a list of ratings for the new user, all_ratings is the dataframe generated from existed users, top_k is the number of nearest neighbors to consider
# MODIFIES: None
# EFFECTS: Predicts ratings for all items for the new user based on the ratings of the nearest neighbors, and returns a list of predicted ratings.
def _predict_ratings(user_vector, all_ratings, top_k=5):
    """Predict ratings for all items using nearest neighbors."""
    similarities = []
    for idx, row in all_ratings.iterrows():
        row_values = [float(x) for x in row]
        sim = cosine_similarity(user_vector, row_values)
        similarities.append((idx, sim, row_values))

    similarities.sort(key=lambda item: item[1], reverse=True)
    # Declares neighbors as those with highest similarity scores above 0.0, up to top_k neighbors
    neighbors = [item for item in similarities if item[1] > 0.0][:top_k]
    # If no neighbors have positive similarity, return a vector of 0s (no predictions)
    if not neighbors:
        return [0.0] * len(user_vector)

    weighted_sum = [0.0] * len(user_vector)
    weight_total = [0.0] * len(user_vector)
    
    # For each neighbor, add their ratings weighted by similarity to the weighted sum
    for _, similarity, neighbor_ratings in neighbors:
        for index, rating in enumerate(neighbor_ratings):
            if rating > 0:
                weighted_sum[index] += similarity * rating
                weight_total[index] += similarity
    # Compute final predictions by dividing the weighted sum by the total weight for each item, handling cases where weight_total is 0 to avoid division by zero.
    predictions = []
    for index in range(len(user_vector)):
        if weight_total[index] > 0:
            predictions.append(weighted_sum[index] / weight_total[index])
        else:
            predictions.append(0.0)

    return predictions


# REQUIRES: user_ratings is a list of (item_id, rating) pairs for the new user, all_ratings is the dataframe of existing user ratings, top_n is the number of recommendations to return, top_k is the number of neighbors to consider
# MODIFIES: None
# EFFECTS: Returns a list of the top recommended item IDs and their predicted scores for the new user based on their ratings and the ratings of similar users.
def recommend_colors(user_ratings, all_ratings, top_n=5, top_k=5):
    """Return the top recommended item IDs and scores for a new user."""
    if len(all_ratings) == 0:
        return []

    if isinstance(user_ratings, (list, tuple)) and len(user_ratings) > 0 and isinstance(user_ratings[0], (list, tuple)):
        user_vector = build_user_vector(user_ratings, n_items=all_ratings.shape[1])
    else:
        user_vector = list(user_ratings)

    predictions = _predict_ratings(user_vector, all_ratings, top_k=top_k)

    for index, rating in enumerate(user_vector):
        if rating > 0:
            predictions[index] = 0.0

    ranked = sorted(enumerate(predictions), key=lambda item: item[1], reverse=True)
    return [(int(item_id), float(score)) for item_id, score in ranked[:top_n] if score > 0.0]


if __name__ == "__main__":
    try:
        gsheets.gsheets_pull()
        df = load_ratings()
        print(f"Loaded {len(df)} user rating rows.")
    except Exception as exc:
        print("Failed to load ratings:", exc)
