import pandas as pd
from data_loading import load_sales_data

def preprocess_sales_data(df):
    # extract only sales from our desired app 
    df = df[df['Product id'] == 'com.vansteinengroentjes.apps.ddfive']
    # group sales by day
    df_day = df.groupby('Transaction Date')['Amount (Merchant Currency)'].sum().reset_index()
    print(df_day[["Transaction Date", "Amount (Merchant Currency)"]])
    df_month

preprocess_sales_data(load_sales_data())
