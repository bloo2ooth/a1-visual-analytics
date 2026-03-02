import pandas as pd
import os

stats_country_files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('stats_ratings') and file.endswith('country.csv')]
df_stats_country = pd.concat([pd.read_csv(f, encoding='utf-16') for f in stats_country_files], ignore_index=True)
# filter for product
df_stats_country = df_stats_country[df_stats_country['Package Name'] == 'com.vansteinengroentjes.apps.ddfive']
df_final = df_stats_country.groupby(['Country']).agg(avg_rating=('Total Average Rating', 'mean')).reset_index()
print(df_final[df_final['avg_rating'] == 5.0])
print(df_final[df_final['avg_rating'] == 1.0])