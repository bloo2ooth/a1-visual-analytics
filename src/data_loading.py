import pandas as pd
import os

def load_review_data():
    review_files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('reviews') and file.endswith('.csv')]
    stats_crashes_files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('stats_crashes') and file.endswith('.csv')]
    df_reviews = pd.concat([pd.read_csv(f, encoding='utf-16') for f in review_files], ignore_index=True)
    df_stats_ratings = pd.concat([pd.read_csv(f, encoding='utf-16') for f in stats_crashes_files], ignore_index=True)
    print(df_stats_ratings.isna().sum())
    print(df_reviews.isna().sum())
    return df_reviews, df_stats_ratings


load_review_data()