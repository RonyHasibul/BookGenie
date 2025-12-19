import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

print("--- Starting Data Preprocessing & Enrichment ---")

# 1. Load the Datasets
books = pd.read_csv('Books Dataset/Books.csv', low_memory=False)
users = pd.read_csv('Books Dataset/Users.csv')
ratings = pd.read_csv('Books Dataset/Ratings.csv')

# 2. Data Cleaning
# Calculate Average Rating and Number of Ratings for SRS 3.1.2
ratings_with_name = ratings.merge(books, on='ISBN')
num_rating_df = ratings_with_name.groupby('Book-Title').count()['Book-Rating'].reset_index()
num_rating_df.rename(columns={'Book-Rating':'num_ratings'}, inplace=True)

avg_rating_df = ratings_with_name.groupby('Book-Title').mean()['Book-Rating'].reset_index()
avg_rating_df.rename(columns={'Book-Rating':'avg_rating'}, inplace=True)

# Merge back into books
books = books.merge(num_rating_df, on='Book-Title').merge(avg_rating_df, on='Book-Title')

# Add Genre placeholder for SRS 3.1.3
if 'Genre' not in books.columns:
    books['Genre'] = 'Fiction'

# 3. Create Popularity Model (Top 50)
popular_df = books[books['num_ratings'] >= 250].sort_values('avg_rating', ascending=False).head(50)

# 4. Collaborative Filtering Logic (Creating the Matrix)
# Filtering users who have rated more than 200 books
x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
educated_users = x[x].index
filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(educated_users)]

# Filtering books with more than 50 ratings
y = filtered_rating.groupby('Book-Title').count()['Book-Rating'] >= 50
famous_books = y[y].index
final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]

pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
pt.fillna(0, inplace=True)

# Calculate Similarity Scores
similarity_scores = cosine_similarity(pt)

# 5. EXPORT EVERYTHING TO PKL
print("--- Exporting Updated .pkl Files ---")
pickle.dump(popular_df, open('popular.pkl', 'wb'))
pickle.dump(pt, open('pt.pkl', 'wb'))
pickle.dump(books[['Book-Title', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating', 'Genre']].drop_duplicates('Book-Title'), open('books.pkl', 'wb'))
pickle.dump(similarity_scores, open('similarity_scores.pkl', 'wb'))

print("Success! All files updated and compatible with the new website features.")