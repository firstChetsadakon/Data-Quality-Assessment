import pandas as pd
import numpy as np
import re
from datetime import datetime


def clean_missing_value(data):
    #=============================================================
    # Step 1 เติม Price Per Unit 
    #=============================================================
    data.loc[data['Price Per Unit'].isna(), 'Price Per Unit'] = data['Total Spent'] / data['Quantity']

    #=============================================================
    # Step 2 เติม Item
    #=============================================================
    # สร้าง mapping ของ Item ตาม Price Per U (เลือก Item แรกที่เจอในข้อมูล)
    price_to_item = data.dropna(subset=['Item']).groupby('Price Per Unit')['Item'].first().to_dict()

    # เติมค่าที่ขาดในคอลัมน์ Item โดยใช้ Price Per U
    data['Item'] = data['Item'].fillna(data['Price Per Unit'].map(price_to_item))

    #=============================================================
    # Step 3 เติม QTY และ Total Spent, Discount
    #=============================================================
    data['Quantity'] = data.groupby('Item')['Quantity'].transform(lambda x: x.fillna(x.mean()))

    # Fill Total Spent
    data["Total Spent"] = data["Price Per Unit"] * data["Quantity"]

    # เติมค่า missing ใน Discount Applied เป็น False
    data["Discount Applied"] = data["Discount Applied"].fillna(False)
    return data


def preprocess_sales_data_flexible(df, n_past_week=6, n_future_week=1, start_date=None, end_date=None):
    """
    Preprocesses the sales dataset to generate time-based features and future sales aggregation.

    Parameters:
    df (pd.DataFrame): The sales data
    n_past_week (int): Number of past weeks to use for features (default=6)
    n_future_week (int): Number of future weeks to predict aggregated sales (default=1)
    start_date (str): Optional start date for filtering data (format: 'YYYY-MM')
    end_date (str): Optional end date for filtering data (format: 'YYYY-MM')

    Returns:
    pd.DataFrame: Processed dataset with time-series features and future target sales
    """
    # Convert Transaction Date to datetime format
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"])

    # Extract Week (starting on Sunday) for aggregation
    df["Year_Week"] = df["Transaction Date"].dt.to_period("W-SUN").apply(lambda x: x.start_time.strftime('%Y-%m-%d'))

    # Convert Discount Applied to binary values (True=1, False=0)
    df["Discount Applied"] = df["Discount Applied"].fillna(False).astype(int)

    # Aggregate basic features
    grouped = df.groupby("Year_Week").agg(
        weekly_avg_repeat_purchases=("Customer ID", lambda x: x.duplicated().mean()),
        total_sales=("Total Spent", "sum"),
        unique_transactions=("Transaction ID", "nunique"),
        unique_customers=("Customer ID", "nunique"),
        discounted_transactions=("Discount Applied", "sum"),
    ).reset_index()

    # Aggregate category sales but shift to keep only t-1 to t-n values
    category_sales = df.groupby(["Year_Week", "Category"])["Total Spent"].sum().unstack(fill_value=0)
    # Shift to remove current week's data

    # Aggregate unique transactions per payment method
    payment_transactions = df.groupby(["Year_Week", "Payment Method"])["Transaction ID"].nunique().unstack(fill_value=0)

    # Aggregate unique transactions per location
    location_transactions = df.groupby(["Year_Week", "Location"])["Transaction ID"].nunique().unstack(fill_value=0)

    # Merge all aggregated data
    final_df = grouped.merge(category_sales, on="Year_Week", how="left") \
        .merge(payment_transactions, on="Year_Week", how="left") \
        .merge(location_transactions, on="Year_Week", how="left")

    # Fill NaNs resulting from merging
    # Allow NaN values for rows without data
    final_df.fillna(float('nan'), inplace=True)

    # Generate past weeks features (t-1 to t-N)
    feature_cols = [col for col in final_df.columns if col != "Year_Week"]
    past_week_cols = ["unique_transactions", "unique_customers", "discounted_transactions"] + feature_cols
    for col in feature_cols:
        for i in range(1, n_past_week + 1):
            final_df[f"{col}_t-{i}"] = final_df[col].shift(i)

    # Generate future target sales (T+1 to T+n_future_week)
    for i in range(1, n_future_week + 1):
        final_df[f"y_{i}"] = (
            final_df["total_sales"].shift(-i)
        )

    # Apply date filtering if specified
    if start_date:
        final_df = final_df[final_df["Year_Week"] >= start_date]
    if end_date:
        final_df = final_df[final_df["Year_Week"] <= end_date]

    return final_df