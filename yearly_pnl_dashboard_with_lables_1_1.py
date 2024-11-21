
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Streamlit app for Yearly P&L Report
def main():
    st.title('Yearly Profit and Loss Dashboard')
    
    # File uploader for Yearly P&L data
    uploaded_file = st.file_uploader("Upload your Yearly Profit and Loss Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # Load the uploaded P&L file into a DataFrame, read values instead of formulas
            pnl_data = pd.read_excel(uploaded_file, sheet_name='Profit and Loss', engine='openpyxl')
            pnl_data = pnl_data.copy()  # Make sure to keep values not formulas
            
            # Check if the DataFrame is empty
            if pnl_data.empty:
                st.error("The uploaded file is empty. Please provide a valid Yearly Profit and Loss Excel file.")
                return
            
            # Data Cleaning and Processing
            pnl_data_cleaned = clean_and_process_data(pnl_data)
            
            # Calculations for Metrics
            metrics = calculate_metrics(pnl_data_cleaned)
            
            # Display and Plot Metrics
            plot_metrics(metrics)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Function to clean and process the data
def clean_and_process_data(df):
    # Remove unnecessary rows, forward fill category information
    df_cleaned = df.dropna(subset=['Jan - Dec 2021', 'Jan - Dec 2022', 'Jan - Dec 2023'], how='all')
    df_cleaned['Category'] = df_cleaned['Unnamed: 0'].ffill()
    df_cleaned = df_cleaned.dropna(subset=['Jan - Dec 2021', 'Jan - Dec 2022', 'Jan - Dec 2023'], how='all')
    df_cleaned.reset_index(drop=True, inplace=True)
    return df_cleaned

# Function to calculate metrics
def calculate_metrics(df):
    years = ['Jan - Dec 2021', 'Jan - Dec 2022', 'Jan - Dec 2023', 'Jan 1 - Nov 12, 2024']
    
    # Extract necessary rows for each metric
    opex_df = df[df['Category'].str.contains("Operating Expenses", case=False, na=False)]
    revenue_df = df[df['Category'].str.contains("Revenue|Income", case=False, na=False)]
    purchase_price_df = df[df['Category'].str.contains("Purchase Price", case=False, na=False)]
    rehab_costs_df = df[df['Category'].str.contains("Rehab Costs", case=False, na=False)]
    sales_price_df = df[df['Category'].str.contains("Sales Price", case=False, na=False)]
    holding_costs_df = df[df['Category'].str.contains("Holding Costs", case=False, na=False)]
    selling_costs_df = df[df['Category'].str.contains("Selling Costs", case=False, na=False)]
    buying_costs_df = df[df['Category'].str.contains("Buying Costs", case=False, na=False)]
    
    # Calculations
    opex_values = holding_costs_df[years].values + selling_costs_df[years].values
    revenue_total = revenue_df.loc[revenue_df['Category'] == 'Total Income'][years].values
    opex_ratio = opex_values / revenue_total * 100
    
    holding_costs_percent_sales = (holding_costs_df[years].values / sales_price_df[years].values) * 100
    average_buy_at = ((purchase_price_df[years].values + rehab_costs_df[years].values) / sales_price_df[years].values) * 100
    selling_costs_percent_sales = (selling_costs_df[years].values / sales_price_df[years].values) * 100
    buying_costs_percent_sales = (buying_costs_df[years].values / sales_price_df[years].values) * 100
    buying_costs_percent_purchase = (buying_costs_df[years].values / purchase_price_df[years].values) * 100
    
    metrics = {
        'OPEX Ratio': opex_ratio,
        'Holding Costs as % of Sales Price': holding_costs_percent_sales,
        'Average % Buy at': average_buy_at,
        'Selling Costs as % of Sales Price': selling_costs_percent_sales,
        'Buying Costs as % of Sales Price': buying_costs_percent_sales,
        'Buying Costs as % of Purchase Price': buying_costs_percent_purchase
    }
    return metrics

# Function to plot metrics
def plot_metrics(metrics):
    years = ['2021', '2022', '2023', '2024']
    
    for metric, values in metrics.items():
        st.subheader(metric)
        plt.figure(figsize=(10, 6))
        for i, year in enumerate(years):
            plt.bar(year, values[0][i])
            plt.text(i, values[0][i] + 0.5, f'{values[0][i]:.2f}%', ha='center', va='bottom')  # Adding labels to bars
        plt.xlabel('Year')
        plt.ylabel(metric)
        plt.title(f'{metric} Over the Years')
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
        st.pyplot(plt)

if __name__ == "__main__":
    main()
    