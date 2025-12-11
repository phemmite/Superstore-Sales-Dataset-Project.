# ===============================================================
# 🧹 Superstore Sales Data Wrangling and KPI Analysis
# ===============================================================
# This notebook demonstrates data cleaning, KPI computation, and visualization
# for the Superstore Sales dataset.

# Sections:
# 1. Data Loading & Cleaning
# 2. KPI Calculation
# 3. Top Products & Regions
# 4. Visualizations
# 5. Save for Power BI/Tableau
# ===============================================================

# --- Setup and Data Loading ---
import pandas as pd
import matplotlib.pyplot as plt

 #----=========================Load dataset
file_path = "Superstore_Cleaned.csv"  # Ensure the CSV is in the same folder
df = pd.read_csv(file_path)
df.head()


#--- 2. Data Cleaning ---
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce', dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce', dayfirst=True)

# Fill missing Postal Codes
if df['Postal Code'].isnull().any():
    df['Postal Code'].fillna(df['Postal Code'].mode()[0], inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Remove rows with invalid date order
df = df[df['Ship Date'] >= df['Order Date']]

# Add time-based features
df['Order Year'] = df['Order Date'].dt.year
df['Order Month'] = df['Order Date'].dt.month
df['Order Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)

print("Cleaned dataset shape:", df.shape)
print(df.info())



# --- 3. KPI Calculation ---
gross_margin = 0.30  # Approximation for CLV proxy

total_revenue = df['Sales'].sum()
orders = df['Order ID'].nunique()
customers = df['Customer ID'].nunique()
aov = total_revenue / orders
avg_orders_per_customer = df.groupby('Customer ID')['Order ID'].nunique().mean()
clv_proxy = aov * avg_orders_per_customer * gross_margin
repeat_rate = (df.groupby('Customer ID')['Order ID'].nunique() > 1).mean()

monthly_revenue = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_revenue['Order Date'] = monthly_revenue['Order Date'].dt.to_timestamp()

kpi_summary = pd.DataFrame({
    'KPI': ['Total Revenue', 'Orders', 'Customers', 'AOV', 'CLV (proxy)', 'Repeat Rate'],
    'Value': [total_revenue, orders, customers, aov, clv_proxy, repeat_rate]
})
print("\n--- KPI Summary ---")
display(kpi_summary)

# --- 4. Top Performing Products & Regions ---
top_products = (
    df.groupby(['Product ID', 'Product Name'])['Sales']
    .sum()
    .reset_index()
    .sort_values('Sales', ascending=False)
    .head(10)
)

top_regions = (
    df.groupby('Region')['Sales']
    .sum()
    .reset_index()
    .sort_values('Sales', ascending=False)
)

print("\nTop 10 Products:")
display(top_products)
print("\nTop Regions:")
display(top_regions)


import matplotlib.pyplot as plt

# --- 5. Visualizations ---
plt.figure(figsize=(10, 5))
plt.plot(monthly_revenue['Order Date'], monthly_revenue['Sales'], marker='o')
plt.title('Monthly Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Sales (USD)')
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
plt.barh(top_products['Product Name'][::-1], top_products['Sales'][::-1])
plt.title('Top 10 Products by Sales')
plt.xlabel('Sales (USD)')
plt.show()

plt.figure(figsize=(6, 4))
plt.bar(top_regions['Region'], top_regions['Sales'])
plt.title('Sales by Region')
plt.ylabel('Sales (USD)')
plt.show()


# --- 6. Save Cleaned Dataset ---
df.to_csv('Superstore_Cleaned.csv', index=False)
print("✅ Cleaned dataset saved as Superstore_Cleaned.csv")
