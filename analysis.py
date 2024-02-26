import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure that all figures show simultaneously
plt.ion()  # Turn on interactive mode

# Create the directory for analysis figures
figures_directory = 'analysis figures'
if not os.path.exists(figures_directory):
    os.makedirs(figures_directory)

# Step 1: Data Loading
# Load the dataset
data = pd.read_csv('sales_data.csv')

# Step 2: Data Cleaning
# Convert 'Date' column to datetime
data['Date'] = pd.to_datetime(data['Date'])

# Identify and handle missing values
data['Quantity Sold'].fillna(data['Quantity Sold'].median(), inplace=True)
data.dropna(subset=['Product', 'Region'], inplace=True)

# Removing outliers for 'Sales Amount' using the IQR method
Q1 = data['Sales Amount'].quantile(0.25)
Q3 = data['Sales Amount'].quantile(0.75)
IQR = Q3 - Q1
data_filtered = data.query('(@Q1 - 1.5 * @IQR) <= `Sales Amount` <= (@Q3 + 1.5 * @IQR)')

# Set 'Date' as the index for resampling
data_filtered.set_index('Date', inplace=True)

# Step 3: Exploratory Data Analysis (EDA)
# Resample and plot daily sales
daily_sales = data_filtered.resample('D')['Sales Amount'].sum()
plt.figure(figsize=(10, 6))  # Adjusting figure size for better readability
daily_sales.plot(kind='bar', title='Daily Sales Amount')  # Using a bar plot for daily data
plt.xlabel('Date')
plt.ylabel('Sales Amount')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()  # Adjust layout to fit labels and title
plt.savefig(os.path.join(figures_directory, 'daily_sales_amount.png'))
plt.close()

# Visualize sales by product
plt.figure(figsize=(10, 6))
sns.barplot(x='Product', y='Sales Amount', data=data_filtered, estimator=sum, ci=None)
plt.title('Total Sales by Product')
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to fit labels and title
plt.savefig(os.path.join(figures_directory, 'total_sales_by_product.png'))
plt.close()

# Step 4: Basic Statistical Analysis
# Calculate basic statistics for 'Sales Amount'
mean_sales = np.mean(data_filtered['Sales Amount'])
median_sales = np.median(data_filtered['Sales Amount'])
std_sales = np.std(data_filtered['Sales Amount'], ddof=1)  # Use ddof=1 for sample standard deviation

# Output basic statistics
print(f"Mean Sales Amount: {mean_sales}")
print(f"Median Sales Amount: {median_sales}")
print(f"Standard Deviation of Sales Amount: {std_sales}")

# Prepare data for t-test
region1_sales = data_filtered[data_filtered['Region'] == 'Region 1']['Sales Amount']
region2_sales = data_filtered[data_filtered['Region'] == 'Region 2']['Sales Amount']

# Perform t-test only if both regions have more than one data point
if len(region1_sales) > 1 and len(region2_sales) > 1:
    t_stat, p_value = stats.ttest_ind(region1_sales, region2_sales, equal_var=False)
    # Output the results of the t-test
    print(f"T-statistic: {t_stat}, P-value: {p_value}")

    # Interpretation of results
    if p_value < 0.05:
        print("There's a statistically significant difference in sales between Region 1 and Region 2.")
    else:
        print("There's no statistically significant difference in sales between Region 1 and Region 2.")
else:
    print("Not enough data to perform a t-test between Region 1 and Region 2.")

plt.ioff()  # Turn off interactive mode
