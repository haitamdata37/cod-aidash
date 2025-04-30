import pandas as pd
import numpy as np
import re
import urllib.parse
import requests
from io import StringIO
from datetime import datetime

def extract_sheet_id(sheet_url):
    """Extract the Google Sheet ID from the URL."""
    pattern = r'/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, sheet_url)
    if match:
        return match.group(1)
    return None

def normalize_string(s):
    """Normalize string for comparison by removing special characters."""
    if isinstance(s, str):
        return re.sub(r'[\'`\'\'""\\s]', '', s.lower())
    return s

def fetch_sheet_data(sheet_url, sheet_name):
    """Fetch data from Google Sheet without using API credentials."""
    try:
        # Extract sheet ID from URL
        sheet_id = extract_sheet_id(sheet_url)
        if not sheet_id:
            return "Invalid Google Sheet URL. Please check the format.", None
        
        # Encode the sheet name
        encoded_sheet_name = urllib.parse.quote(sheet_name)
        
        # Construct the CSV export URL
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
        
        # Fetch the CSV data
        response = requests.get(csv_export_url)
        
        if response.status_code != 200:
            return f"Error: Unable to access the Google Sheet. Status code: {response.status_code}", None
        
        # Parse the CSV data - specify header=None to prevent auto-header detection
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data, header=None)
        
        # Check if we got valid data
        if df.empty:
            return "No data found in the sheet or sheet is empty.", None
        
        # Set header row and get data rows
        headers = df.iloc[0].values
        headers = [str(col).strip() for col in headers]
        data = df.iloc[1:].copy()
        data.columns = headers
        data = data.reset_index(drop=True)
        
        return "Successfully fetched data!", data
    
    except Exception as e:
        return f"Error: {str(e)}", None

def clean_numeric_column(series):
    """
    Clean numeric column by removing currency symbols and commas
    
    Args:
        series (pd.Series): Input series to clean
    
    Returns:
        pd.Series: Cleaned numeric series
    """
    # Convert to string first
    series = series.astype(str)
    
    # Remove currency symbols, spaces, and thousand separators
    series = series.str.replace('dh', '', case=False)
    series = series.str.replace(',', '')
    
    # Convert to numeric
    return pd.to_numeric(series, errors='coerce').fillna(0)

def process_stock_data(df):
    """Process stock data and add calculated fields."""
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid warnings
    processed_df = df.copy()
    
    # Convert numeric columns
    numeric_columns = ['Quantité achetée', 'Quantité commandée', 'Quantité disponible']
    for col in numeric_columns:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').fillna(0)
    
    # Add price column if not exists (for simplicity)
    if 'Prix' not in processed_df.columns and 'Prix produit' in processed_df.columns:
        processed_df['Prix'] = clean_numeric_column(processed_df['Prix produit'])
    
    return processed_df

def process_orders_data(df):
    """Process orders data and add calculated fields."""
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid warnings
    processed_df = df.copy()
    
    # Process dates - with better conversion for French date format
    date_cols = [col for col in processed_df.columns if 'date' in col.lower()]
    for col in date_cols:
        try:
            # Try to detect and convert date formats (handling both DD/MM/YYYY and YYYY-MM-DD)
            # First, check the format of a few samples to decide how to parse
            sample_dates = processed_df[col].astype(str).dropna().head(5).tolist()
            print(f"Sample dates for {col}: {sample_dates}")
            
            # Try to determine format
            if any('/' in str(date) for date in sample_dates):
                # Likely DD/MM/YYYY format
                processed_df[col] = pd.to_datetime(processed_df[col], format='%d/%m/%Y', errors='coerce')
                print(f"Converted {col} using DD/MM/YYYY format")
            else:
                # Try standard parsing
                processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
                print(f"Converted {col} using standard parsing")
                
            # Print a sample of converted dates
            print(f"After conversion, {col} sample: {processed_df[col].head().tolist()}")
        except Exception as e:
            print(f"Error converting dates for column {col}: {str(e)}")
    
    # Process price and amount columns
    price_cols = [col for col in processed_df.columns if 'prix' in col.lower() or 'montant' in col.lower()]
    for col in price_cols:
        processed_df[col] = clean_numeric_column(processed_df[col])
    
    return processed_df

def process_supplier_data(df):
    """Process supplier data and add calculated fields."""
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid warnings
    processed_df = df.copy()
    
    # Process dates - with better conversion for French date format
    date_cols = [col for col in processed_df.columns if 'date' in col.lower()]
    for col in date_cols:
        try:
            # Try to detect and convert date formats (handling both DD/MM/YYYY and YYYY-MM-DD)
            # First, check the format of a few samples to decide how to parse
            sample_dates = processed_df[col].astype(str).dropna().head(5).tolist()
            print(f"Sample dates for {col}: {sample_dates}")
            
            # Try to determine format
            if any('/' in str(date) for date in sample_dates):
                # Likely DD/MM/YYYY format
                processed_df[col] = pd.to_datetime(processed_df[col], format='%d/%m/%Y', errors='coerce')
                print(f"Converted {col} using DD/MM/YYYY format")
            else:
                # Try standard parsing
                processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
                print(f"Converted {col} using standard parsing")
                
            # Print a sample of converted dates
            print(f"After conversion, {col} sample: {processed_df[col].head().tolist()}")
        except Exception as e:
            print(f"Error converting dates for column {col}: {str(e)}")
    
    # Process price and amount columns
    price_cols = [col for col in processed_df.columns if 'prix' in col.lower() or 'montant' in col.lower() or 'reste' in col.lower()]
    for col in price_cols:
        processed_df[col] = clean_numeric_column(processed_df[col])
    
    return processed_df