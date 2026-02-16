import pandas as pd
import os

def load_sales_data():
    # load all sales csv files
    files = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('sales')]
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    return df