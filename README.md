# 🛒 Retail Sales Data Quality Check

## 📌 Project Overview
This project implements a comprehensive data quality assessment for retail store sales data. It evaluates various aspects of data quality, including missing values, format validation, and logical consistency checks to ensure the dataset is suitable for further analysis.

## 📊 Dataset
The dataset (`retail_store_sales.csv`) contains retail transaction records with the following columns:
- Transaction ID
- Customer ID
- Category
- Item
- Price Per Unit
- Quantity
- Total Spent
- Payment Method
- Location
- Transaction Date
- Discount Applied

## 🔍 Data Quality Checks Performed

### ✅ 1. Missing Value Analysis
- Identifies the percentage of missing values in each column
- Highlighted columns with significant missing data:
    - Discount Applied: 33.39%
    - Item: 9.65%
    - Price Per Unit: 4.84%
    - Quantity: 4.80%
    - Total Spent: 4.80%

### ✅ 2. Negative Value Detection
- Checks for negative values in numerical columns (Price Per Unit, Quantity, Total Spent)
- No negative values were found in the dataset

### ✅ 3. ID Format Validation
- Transaction ID format validation (pattern: `TXN_` followed by 7 digits)
- Customer ID format validation (pattern: `CUST_` followed by 2 digits)
- All IDs conform to their expected formats (100% validation rate)

### ✅ 4. Item Code Format Validation
- Item code format validation (pattern: `Item_` followed by numbers and category code)
- All non-missing item codes conform to the expected format

### ✅ 5. Date Format and Validity Check
- Transaction Date format validation (YYYY-MM-DD)
- Verifies that dates are valid calendar dates
- All dates in the dataset are valid

### ✅ 6. Categorical Value Consistency
- Validates consistency in categorical columns (Payment Method, Category, Location)
- All categorical values are consistent throughout the dataset

## 📦 Project Structure
```
📦 Retail-Sales-Data-Quality
├── 📂 data/                     # Folder containing raw data
│   ├── retail_store_sales.csv   # Retail sales dataset
├── 📜 README.md                 # Project documentation
├── 📜 requirements.txt          # Dependencies required for the project
└── 📜 Retail_Sales_Data_Quality_Check.ipynb  # Jupyter Notebook for data analysis
```

## 🛠 Dependencies
- pandas
- matplotlib
- re (Regular Expressions)
- datetime
- pandas-profiling (for comprehensive profiling, optional)

## 🚀 Installation & Usage
### **1️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **2️⃣ Run the Analysis**
1. Place the `retail_store_sales.csv` file in the `data/` directory
2. Open and run the Jupyter notebook `Retail_Sales_Data_Quality_Check.ipynb`
3. All data quality checks will be executed automatically

## 📊 Key Findings
- The dataset generally has good quality with proper formatting ✅
- The Discount Applied column has a high percentage of missing values (33.39%) ⚠️
- Item codes are missing for about 9.65% of transactions ⚠️
- Numerical data (prices, quantities) are consistent with no negative values ✅
- All IDs and dates follow the expected formats ✅

## 💡 Recommendations
- Consider a strategy for handling missing values in the Discount Applied column
- Investigate the cause of missing Item codes in approximately 10% of records
- The dataset is suitable for analysis after addressing the missing value issues

## 🔮 Future Improvements
- Implement automated data validation pipeline
- Create a dashboard for visualizing data quality metrics
- Integrate with data preprocessing workflows for seamless analysis

🚀 **Ready for data analysis! Feel free to contribute or report any issues.**
