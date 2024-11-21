
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Load the P&L Excel data
pnl_file_path = 'Gould+and+Son+Realty+LLC_Profit+and+Loss.xlsx'

# Streamlit app
def main():
    st.title('Profit and Loss Dashboard')
    
    # File uploader for P&L data
    uploaded_file = st.file_uploader("Upload your Profit and Loss Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # Load the uploaded P&L file into a DataFrame, read values instead of formulas
            pnl_data = pd.read_excel(uploaded_file, sheet_name='Profit and Loss', engine='openpyxl')
            pnl_data = pnl_data.copy()  # Make sure to keep values not formulas
            
            # Check if the DataFrame is empty
            if pnl_data.empty:
                st.error("The uploaded file is empty. Please provide a valid Profit and Loss Excel file.")
                return
            
            # Plotting Net Income
            plot_row(pnl_data, row_index=209, title='Monthly Net Income', label='Net Income', y_limit_buffer=10000)
            
            # Plotting Gross Profit
            gross_profit_row = pnl_data[pnl_data.iloc[:, 0].str.contains('Gross Profit', case=False, na=False)]
            if not gross_profit_row.empty:
                plot_row_data(gross_profit_row.iloc[0, 1:-1], title='Monthly Gross Profit', label='Gross Profit', y_limit_buffer=10000)
            else:
                st.error("Gross Profit data not found in the provided file.")
            
            # Plotting Total METUO + Total Other Expenses
            metuoe_expenses = pnl_data[pnl_data.iloc[:, 0].str.contains('Total METUO', case=False, na=False)]
            other_expenses = pnl_data[pnl_data.iloc[:, 0].str.contains('Total Other Expenses', case=False, na=False)]
            if not metuoe_expenses.empty and not other_expenses.empty:
                combined_expenses = metuoe_expenses.iloc[0, 1:-1] + other_expenses.iloc[0, 1:-1]
                min_value = combined_expenses.min()
                plot_row_data(combined_expenses, title='Monthly METUO + Other Expenses', label='METUO + Other Expenses', y_limit_buffer=10000, y_min_limit=min_value)
            else:
                st.error("Total METUO or Total Other Expenses data not found in the provided file.")
            
            # Plotting All Expenses minus METUO + Other Expenses
            if not metuoe_expenses.empty and not other_expenses.empty:
                total_expenses = pnl_data[pnl_data.iloc[:, 0].str.contains('Total Expenses', case=False, na=False)]
                if not total_expenses.empty:
                    total_expenses_data = total_expenses.iloc[0, 1:-1]
                    combined_metuoe_expenses = metuoe_expenses.iloc[0, 1:-1] + other_expenses.iloc[0, 1:-1]
                    all_expenses_minus_metuoe = total_expenses_data - combined_metuoe_expenses
                    min_value = all_expenses_minus_metuoe.min()
                    plot_row_data(all_expenses_minus_metuoe, title='Monthly All Expenses Minus METUO + Other Expenses', label='Expenses - METUO + Other', y_limit_buffer=10000, y_min_limit=min_value)
                else:
                    st.error("Total Expenses data not found in the provided file.")
            else:
                st.error("Total METUO or Total Other Expenses data not found in the provided file.")
            
            # Plotting ROE
            roe_row = pnl_data[pnl_data.iloc[:, 0].str.contains('ROE', case=False, na=False)]
            if not roe_row.empty:
                plot_row_data(roe_row.iloc[0, 1:-1], title='Monthly Return on Equity (ROE)', label='ROE', y_limit_buffer=0.1)
            else:
                st.error("ROE data not found in the provided file.")
            
        except Exception as e:
            st.error(f"Error processing the P&L file: {e}")
    else:
        st.info('Please upload a Profit and Loss file to begin.')

def plot_row(df, row_index, title, label, y_limit_buffer):
    # Extract specified row
    if len(df) <= row_index:
        st.error(f"The provided file does not have enough rows to extract {label} data from row {row_index + 1}.")
        return
    
    row_data = df.iloc[row_index]
    # Extract monthly data
    data = row_data[1:-1]
    
    # Ensure numeric data and handle missing values
    data = pd.to_numeric(data, errors='coerce').fillna(0)
    
    # Check if there is any valid data to plot
    if data.sum() == 0:
        st.warning(f"The {label} data contains only zeros. Please provide a file with valid {label} values.")
        return
    
    # Define colors for the bars (medium green for positive, light red for negative)
    colors = ['mediumseagreen' if value >= 0 else 'lightcoral' for value in data.values]
    
    # Plotting the data as a bar graph
    fig, ax = plt.subplots(figsize=(14, 10))  # Increase figure size for more space between labels
    bars = ax.bar(data.index, data.values, color=colors, label=label)
    ax.set_xlabel('Month')
    ax.set_ylabel(f'{label} ($)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y')
    ax.legend()  # Add legend to the chart
    
    # Set y-axis limits
    max_value = data.max()
    min_value = -100000
    ax.set_ylim(min_value, max_value + y_limit_buffer)
    
    # Format the y-axis values
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    
    # Add data labels to each bar with offset to avoid overlapping
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + (0.05 * max_value), f'${yval:,.2f}', ha='center', va='bottom', fontsize=10)  # Add offset to labels
    
    # Adjust layout to ensure labels fit well
    plt.tight_layout()
    
    # Show plot in Streamlit
    st.pyplot(fig)

def plot_combined_rows(df, row_indices, title, label, y_limit_buffer):
    # Extract specified rows and combine
    combined_data = pd.Series(dtype=float)
    for row_index in row_indices:
        if len(df) <= row_index:
            st.error(f"The provided file does not have enough rows to extract data from row {row_index + 1}.")
            return
        row_data = df.iloc[row_index][1:-1]
        row_data = pd.to_numeric(row_data, errors='coerce').fillna(0)
        if combined_data.empty:
            combined_data = row_data
        else:
            combined_data += row_data
    
    # Plot the combined rows
    plot_row_data(combined_data, title, label, y_limit_buffer)

def plot_row_data(data, title, label, y_limit_buffer, y_min_limit=None):
    # Ensure numeric data and handle missing values
    data = pd.to_numeric(data, errors='coerce').fillna(0)
    
    # Check if there is any valid data to plot
    if data.sum() == 0:
        st.warning(f"The {label} data contains only zeros. Please provide a file with valid {label} values.")
        return
    
    # Define colors for the bars (medium green for positive, light red for negative)
    colors = ['mediumseagreen' if value >= 0 else 'lightcoral' for value in data.values]
    
    # Plotting the data as a bar graph
    fig, ax = plt.subplots(figsize=(14, 10))  # Increase figure size for more space between labels
    bars = ax.bar(data.index, data.values, color=colors, label=label)
    ax.set_xlabel('Month')
    ax.set_ylabel(f'{label} ($)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y')
    ax.legend()  # Add legend to the chart
    
    # Set y-axis limits
    max_value = data.max()
    min_value = y_min_limit if y_min_limit is not None else -100000
    ax.set_ylim(min_value, max_value + y_limit_buffer)
    
    # Format the y-axis values
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    
    # Add data labels to each bar with offset to avoid overlapping
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + (0.05 * max_value), f'${yval:,.2f}', ha='center', va='bottom', fontsize=10)  # Add offset to labels
    
    # Adjust layout to ensure labels fit well
    plt.tight_layout()
    
    # Show plot in Streamlit
    st.pyplot(fig)

if __name__ == "__main__":
    main()
