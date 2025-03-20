import pandas as pd
import numpy as np
import re
from datetime import datetime


def check_uniqueness(df):
    output = df.copy()
    output['uniqueness_flag'] = ~output.duplicated(keep='first')
    return output


def is_valid_date(date_str):
    """ ตรวจสอบว่า date_str อยู่ในรูปแบบ YYYY-MM-DD และเป็นวันที่ที่ถูกต้อง """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def check_total_spent(row):
    """
    ตรวจสอบว่า Total Spent = Price Per Unit * Quantity หรือไม่
    หากไม่สามารถตรวจสอบได้ ให้ return 'CANT CHECK'
    """
    if pd.isna(row['Total Spent']):
        return np.nan  # ถ้า Total Spent เป็น NaN ให้ return missing value
    
    elif not isinstance(row['Total Spent'], (int, float)):  # ตรวจสอบว่า Total Spent เป็นตัวเลขหรือไม่
        return False  # หากไม่ใช่ตัวเลขให้ return False
    
    elif pd.isna(row['Price Per Unit']) or pd.isna(row['Quantity']):
        return 'CANT CHECK'  # ถ้า Price Per Unit หรือ Quantity เป็น NaN ให้ return CANT CHECK
    
    # ตรวจสอบว่า Total Spent = Price Per Unit * Quantity
    elif row['Total Spent'] == row['Price Per Unit'] * row['Quantity']:
        return True
    else:
        return False


def check_price_validity(row, master_price_df):
    """
    ตรวจสอบความถูกต้องของ Price Per Unit ตามเงื่อนไข:
    - ถ้า Price Per Unit เป็น missing value ให้ return np.nan
    - ถ้า Price Per Unit ไม่ใช่ float หรือ int หรือมีค่าน้อยกว่าหรือเท่ากับ 0 ให้ return False
    - ถ้า Item, Transaction Date หาย หรือ Transaction Date_vailidity ไม่เป็น True ให้ return 'CANT CHECK'
    - ถ้า Item ไม่มีใน master data ให้ return 'CANT CHECK'
    - ถ้าไม่มีราคาที่ตรงกับ Transaction Date ในช่วง Start_date - End_date ให้ return 'CANT CHECK'
    - ถ้า Price Per Unit ตรงกับราคาใน master data ช่วงวันที่ที่กำหนด ให้ return True, ถ้าไม่ตรงให้ return False
    """

    price = row['Price Per Unit']
    item = row['Item']
    transaction_date = row['Transaction Date']

    # 1. ตรวจสอบว่า Price Per Unit เป็น missing value หรือไม่
    if pd.isna(price):
        return np.nan  

    # 2. ตรวจสอบว่า Price Per Unit เป็น float หรือ int และต้องมากกว่า 0
    elif not isinstance(price, (int, float)) or price <= 0:
        return False  

    # 3. ตรวจสอบว่ามี Item, Transaction Date และ Transaction Date_vailidity เป็น True หรือไม่
    elif pd.isna(item) or pd.isna(transaction_date) or (row.get('Transaction Date_vailidity') != True):
        return 'CANT CHECK'  

    else:
        # 4. ตรวจสอบว่า Item มีอยู่ใน master_price_df หรือไม่
        item_prices = master_price_df[master_price_df['Item'] == item]
        if item_prices.empty:
            return 'CANT CHECK'

        # 5. ตรวจสอบว่า Transaction Date อยู่ในช่วง Start_date - End_date หรือไม่
        valid_prices = item_prices[
            (item_prices['Start_date'] <= transaction_date) & 
            (transaction_date <= item_prices['End_date'])
        ]

        if valid_prices.empty:
            return 'CANT CHECK'  # ไม่มีราคาสำหรับช่วงเวลานั้น

        # 6. ตรวจสอบว่า Price Per Unit ตรงกับ master data หรือไม่
        return price in valid_prices['Price Per Unit'].values



def add_validity_column(df, col, rule):
    """
    ตรวจสอบค่าภายในคอลัมน์ว่า valid หรือไม่ ตามกฎที่กำหนด
    - ถ้า rule เป็น string → ใช้ regex ตรวจสอบ pattern
    - ถ้า rule เป็น list → ตรวจสอบค่าต้องอยู่ใน list
    - ถ้า rule เป็น 'integer_non_negative' → ตรวจสอบว่าเป็นเลขจำนวนเต็มที่ไม่ติดลบ
    - ถ้า rule เป็น 'float_non_negative' → ตรวจสอบว่าเป็นตัวเลข (int หรือ float) และไม่ติดลบ
    - ถ้า rule เป็น 'datetime_format' → ตรวจสอบว่ามีรูปแบบ YYYY-MM-DD หรือไม่

    Parameters:
    df (pd.DataFrame): DataFrame ที่ต้องการตรวจสอบ
    col (str): ชื่อคอลัมน์ที่ต้องการตรวจสอบ
    rule (str | list): ถ้าเป็น string → ตรวจสอบด้วย regex, ถ้าเป็น list → ตรวจสอบค่าที่กำหนด, ถ้าเป็น 'integer_non_negative' หรือ 'float_non_negative' → ตรวจสอบค่าที่เป็นตัวเลขและไม่ติดลบ

    Returns:
    pd.DataFrame: DataFrame ที่เพิ่มคอลัมน์ใหม่ {col}_validity
    """
    df = df.copy()  # ป้องกันการแก้ไข DataFrame ต้นฉบับ
    
    if isinstance(rule, str):  
        if rule == 'datetime_format':  
            # ตรวจสอบว่าเป็นวันที่รูปแบบ YYYY-MM-DD หรือไม่
            df[f'{col}_validity'] = df[col].apply(
                                        lambda x: np.nan if pd.isna(x) 
                                        else (bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(x))) and is_valid_date(str(x)))
                                    )
        elif rule == 'integer_non_negative':  
            # ต้องเป็นจำนวนเต็ม (int) และห้ามติดลบ
            df[f'{col}_validity'] = df[col].apply(
                    lambda x: np.nan if pd.isna(x) 
                    else (False if not isinstance(x, (int, float)) else (x == int(x) and x >= 0))
                )
        elif rule == 'float_non_negative':  
            # ต้องเป็นตัวเลข (int หรือ float) และห้ามติดลบ
            df[f'{col}_validity'] = df[col].apply(lambda x: isinstance(x, (int, float)) and x >= 0)
        else:
            # ถ้า rule เป็น regex (string)
            df[f'{col}_validity'] = df[col].astype(str).apply(lambda x: bool(re.fullmatch(rule, x)))
    
    elif isinstance(rule, list):  
        # ถ้า rule เป็น list → ตรวจสอบว่าค่าอยู่ใน list หรือไม่
        df[f'{col}_validity'] = df[col].where(df[col].isna(), df[col].isin(rule))
    
    return df

def add_missing_indicators(df):
    """
    เพิ่มคอลัมน์ที่บ่งบอกว่าแต่ละคอลัมน์มี missing values หรือไม่

    Parameters:
    df (pd.DataFrame): DataFrame ที่ต้องการตรวจสอบค่า Missing

    Returns:
    pd.DataFrame: DataFrame ที่เพิ่มคอลัมน์ *_completeness ที่มีค่า True/False
    """
    df = df.copy()  # ป้องกันการแก้ไข DataFrame ต้นฉบับ    
    for col in df.columns.difference(['uniqueness_flag']):
        df[f'{col}_completeness'] = df[col].notnull()
    return df

def check_item_validity(row, abbrev_dict):
    """
    ตรวจสอบว่า value ใน column 'Item' มีรูปแบบ Item_{เลขกี่ตัวก็ได้}_{ตัวหนังสือกี่ตัวก็ได้} หรือไม่
    - ถ้า Item เป็น missing value ให้ return np.nan
    - ถ้า Item ไม่ตรงกับ pattern Item_{เลข}_{ตัวหนังสือ} ให้ return False
    - ถ้า Category เป็น missing value ให้ return 'CANT CHECK'
    - ถ้า Category ไม่มีตัวย่อใน abbrev_dict ให้ return 'CANT CHECK'
    - ถ้า Item ตรงกับ pattern Item_\d+_{category_abbrev} ให้ return True
    """

    item = row['Item']
    category = row['Category']

    if pd.isna(item):  
        return np.nan  # 1. ถ้า Item เป็น NaN ให้ return NaN

    elif not re.fullmatch(r"Item_\d+_[A-Za-z]+", item):  
        return False  # 2. ถ้า Item ไม่ตรง pattern Item_{เลข}_{ตัวหนังสือ} ให้ return False

    elif pd.isna(category):  
        return 'CANT CHECK'  # 3. ถ้า Category เป็น NaN ให้ return 'CANT CHECK'

    elif category not in abbrev_dict:  
        return 'CANT CHECK'  # 4. ถ้าไม่มีตัวย่อ category ใน dict ให้ return 'CANT CHECK'

    else:
        # 5. ตรวจสอบว่า Item ตรงกับ pattern Item_\d+_{category_abbrev} หรือไม่
        category_abbrev = abbrev_dict[category]
        pattern = rf"Item_\d+_{category_abbrev}"
        return True if re.fullmatch(pattern, item) else False


def check_data_vailidy(data,master_price_df):
    # List ของข้อมูลที่ Valid ในแต่ละ Column
    category_list = ['Patisserie','Milk Products','Butchers','Beverages','Food','Furniture','Electric household essentials','Computers and electric accessories']
    payment_method_list = ['Digital Wallet', 'Credit Card', 'Cash']
    location_list = ['Online', 'In-store']
    discount_applied_list = [True,False]

    # Dict ตัวย่อของแต่ละ Category
    abbrev_dict = {
        'Patisserie': 'PAT',
        'Milk Products': 'MILK',
        'Butchers': 'BUT',
        'Beverages': 'BEV',
        'Food': 'FOOD',
        'Furniture': 'FUR',
        'Electric household essentials': "EHE",
        'Computers and electric accessories': "CEA"
    }


    # Rule ในการ Check Validity
    validation_rules = {
        'Transaction ID': r'TXN_\d{7}',  # ต้องเป็น TXN_ ตามด้วยเลข 7 ตัว (ใช้ regex)
        'Customer ID': r'^CUST_\d+$',      # ต้องเป็น CUST_ ตามด้วยเลขกี่ตัวก็ได้ (ใช้ regex)
        'Category': category_list,  # ต้องอยู่ใน list ที่กำหนด
        'Payment Method' : payment_method_list,  # ต้องอยู่ใน list ที่กำหนด
        'Location' : location_list, # ต้องอยู่ใน list ที่กำหนด
        'Discount Applied': discount_applied_list, # ต้องอยู่ใน list ที่กำหนด
        'Quantity': 'integer_non_negative',  # ต้องเป็นจำนวนเต็ม และห้ามติดลบ
        # 'Price Per Unit': 'float_non_negative', # ต้องเป็น float หรือ int และห้ามติดลบ
        'Transaction Date': 'datetime_format',  # ต้องเป็น YYYY-MM-DD
    }


    output = data.copy()

    #=============================================================
    # Step 1 Completeness: ตรวจ Check Missing Value ในแต่ละ Column
    #=============================================================
    output = add_missing_indicators(output)

    #=============================================================
    # Step 2 Validity : ตรวจ Validity ในแต่ละ Column
    #=============================================================
    # ใช้ for loop เพื่อตรวจสอบ validity ในแต่ละคอลัมน์
    for col, pattern in validation_rules.items():
        output = add_validity_column(output, col, pattern)

    # เพิ่ม column เพื่อตรวจสอบ validity
    output['Item_validity'] = output.apply(check_item_validity,abbrev_dict=abbrev_dict, axis=1)
    output['Price Per Unit_validity'] = output.apply(check_price_validity,master_price_df = master_price_df,axis=1)
    output['Total Spent_validity'] = output.apply(check_total_spent, axis=1)
    return output

