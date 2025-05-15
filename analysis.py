import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from fpdf import FPDF
from datetime import datetime

# Set Seaborn theme
sns.set_theme(style="whitegrid")

# Define the path to your CSV file
csv_file = 'Sample.csv'  # Replace with your CSV file

# Get base name for output folder
csv_name = os.path.splitext(os.path.basename(csv_file))[0]
output_root = os.path.join('analysis_output', csv_name)

# Create subdirectories for figures and report
figures_dir = os.path.join(output_root, 'figures')
reports_dir = os.path.join(output_root, 'reports')
os.makedirs(figures_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

# Load the dataset
try:
    data = pd.read_csv(csv_file)
except Exception as e:
    print(f"Error loading CSV file: {e}")
    exit()

# Initialize PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, f'Data Analysis Report: {os.path.basename(csv_file)}', ln=True, align='C')
pdf.ln(10)

# Add basic info
pdf.set_font("Arial", '', 12)
pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
pdf.cell(0, 10, f'Total Rows: {data.shape[0]}, Total Columns: {data.shape[1]}', ln=True)
pdf.ln(10)

# Identify column types
numerical_cols = data.select_dtypes(include=np.number).columns.tolist()
categorical_cols = data.select_dtypes(include='object').columns.tolist()

# Handle missing values
missing_values = data.isnull().sum()
missing_values = missing_values[missing_values > 0]
if not missing_values.empty:
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'Missing Values:', ln=True)
    pdf.set_font("Arial", '', 12)
    for col, count in missing_values.items():
        pdf.cell(0, 10, f'{col}: {count} missing values', ln=True)
    pdf.ln(10)
    # Fill numeric missing with median, drop rows with missing categoricals
    for col in numerical_cols:
        if col in missing_values:
            data[col].fillna(data[col].median(), inplace=True)
    data.dropna(subset=[col for col in categorical_cols if col in missing_values], inplace=True)

# Descriptive stats
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, 'Descriptive Statistics:', ln=True)
pdf.ln(5)
desc_stats = data[numerical_cols].describe().round(2)
pdf.set_font("Arial", '', 10)
for col in desc_stats.columns:
    pdf.cell(0, 10, f'{col}:', ln=True)
    for stat in desc_stats.index:
        pdf.cell(0, 10, f'   {stat}: {desc_stats.at[stat, col]}', ln=True)
    pdf.ln(5)

# Histograms
for col in numerical_cols:
    plt.figure(figsize=(6, 4))
    sns.histplot(data[col], kde=True, bins=30)
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    fig_path = os.path.join(figures_dir, f'{col}_hist.png')
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()

    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f'Distribution of {col}', ln=True)
    pdf.image(fig_path, w=180)
    pdf.ln(10)

# Bar plots
for col in categorical_cols:
    plt.figure(figsize=(6, 4))
    data[col].value_counts().plot(kind='bar')
    plt.title(f'Value Counts of {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    fig_path = os.path.join(figures_dir, f'{col}_bar.png')
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()

    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f'Value Counts of {col}', ln=True)
    pdf.image(fig_path, w=180)
    pdf.ln(10)

# Save PDF
report_path = os.path.join(reports_dir, f'{csv_name}_analysis_report.pdf')
pdf.output(report_path)
print(f'Report generated and saved to: {report_path}')
