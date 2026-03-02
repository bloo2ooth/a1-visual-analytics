import pandas as pd
import os

def load_review_data():
    # collect review, crash and ratings country file paths
    review_files  = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('reviews') and file.endswith('.csv')]
    crashes_files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('stats_crashes') and file.endswith('.csv')]
    # load ratings per country files separately from crash files
    ratings_files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if 'ratings' in file and file.endswith('country.csv')]
    # read and concatenate all files per type
    df_reviews         = pd.concat([pd.read_csv(f, encoding='utf-16') for f in review_files], ignore_index=True)
    df_crashes         = pd.concat([pd.read_csv(f, encoding='utf-16') for f in crashes_files], ignore_index=True)
    df_ratings_country = pd.concat([pd.read_csv(f, encoding='utf-16') for f in ratings_files], ignore_index=True)
    return df_reviews, df_crashes, df_ratings_country
