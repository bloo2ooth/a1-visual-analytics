import pandas as pd
import os

def preprocess_sales_data():
    # get the first four csv sale files as they have same format
    files_f1 = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('sales') and file.endswith('f1.csv')]
    files_f2 = ["Data/assignment1_data/" + file for file in os.listdir('Data/assignment1_data') if file.startswith('sales') and file.endswith('f2.csv')]
    df1 = pd.concat(map(pd.read_csv, files_f1), ignore_index=True)
    df2 = pd.concat(map(pd.read_csv, files_f2), ignore_index=True)
    # change column names to match format 1
    df2.rename(columns={'Order Charged Date': 'Transaction Date',  'Financial Status': 'Transaction Type', 'Currency of Sale': 'Buyer Currency', \
                        'Charged Amount': 'Amount (Buyer Currency)', 'SKU ID': 'Sku Id', 'Postal Code of Buyer': 'Buyer Postal Code',
                        'Product ID': 'Product id', 'Country of Buyer': 'Buyer Country'}, inplace=True)
    # Add merchant currency to format2
    # load fx tabel
    fx = pd.read_csv("Data/eurofxref-hist.csv")
    # get necessary dates from df2
    all_dates = pd.DataFrame({'Date': pd.date_range(df2['Transaction Date'].min(), df2['Transaction Date'].max(), freq='D')})
    all_dates['Date'] = all_dates['Date'].dt.strftime('%Y-%m-%d') 
    # sort by date and fill with last know value
    fx = all_dates.merge(fx, on='Date', how='left')
    fx = fx.sort_values('Date').fillna(method='ffill') 
    # rename date column
    fx.rename(columns={'Date': 'Transaction Date'}, inplace=True)
    # add euro conversion to eur for easier merging later
    fx['EUR'] = 1.0
    # convert fx 
    fx = fx.melt(id_vars=['Transaction Date'], var_name='Buyer Currency', value_name='Currency Conversion Rate')    
    # merge fx with df2
    df2 = df2.merge(fx[['Transaction Date', 'Buyer Currency', 'Currency Conversion Rate']], on=['Transaction Date', 'Buyer Currency'], how='left')
    # add merchant currency for completeness
    df2['Merchant Currency'] = 'EUR'
    # remove comma from buyer amount and convert to float
    df2['Amount (Buyer Currency)'] = df2['Amount (Buyer Currency)'].str.replace(',', '')
    df2['Amount (Buyer Currency)'] = df2['Amount (Buyer Currency)'].astype(float)
    #df2['Currency Conversion Rate'] = df2['Currency Conversion Rate'].astype(float)
    df2['Amount (Merchant Currency)'] = df2['Amount (Buyer Currency)'] / df2['Currency Conversion Rate']
    # filter for necessary columns in both dataframes before merging them
    df1 = df1[['Transaction Date', 'Transaction Type', 'Product id', 'Sku Id', 'Buyer Country', 'Buyer Postal Code', 'Amount (Merchant Currency)', 'Merchant Currency']]
    df2 = df2[['Transaction Date', 'Transaction Type', 'Product id', 'Sku Id', 'Buyer Country', 'Buyer Postal Code', 'Amount (Merchant Currency)', 'Merchant Currency']]
    df_complete = pd.concat([df1, df2], ignore_index=True)
    # save final file
    df_complete.to_csv("Data/processed_sales_data.csv", index=False)

preprocess_sales_data()