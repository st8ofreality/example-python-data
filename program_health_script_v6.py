import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import chardet


def load_file(input_file_path, file_extension):
    if file_extension == '.xlsx':
        return pd.read_excel(input_file_path, engine='openpyxl') # Specifying engine for xlsx
    elif file_extension == '.csv':
        with open(input_file_path, 'rb') as f: 
                readshortversion = chardet.detect(f.read(10000))
                encoding =  readshortversion['encoding']
        return pd.read_csv(input_file_path, encoding=encoding)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

def generate_program_health_report(df, output_dir, file_name_without_extension):
    status_columns = ['NHO', 'Agent', 'Spec 1', 'Spec 2', 'Spec 3']
    eligible_statuses = ["Completed", "On Track", "Working On Tickets", "Training Behind", "Certification Behind", "Not Started"]

    # Create the 'Weeks Category' column
    df['Weeks Category'] = ['<= 16' if x <=16 else '> 16' for x in df['Adjusted Wks']]

    # Melt the dataframe to long format to combine eligible_statuses
    df_melted = df.melt(id_vars=['Weeks Category', 'Role'], value_vars=status_columns, var_name='Full Name', value_name='Status')

    # Filter by eligible statuses
    df_filtered = df_melted[df_melted['Status'].isin(eligible_statuses)]

    # Check if df_filtered is not empty
    if df_filtered.empty:
        print("No data available for the given eligible statuses.")
        return
    
    # Create a pivot table
    pivot_table = pd.pivot_table(df_filtered, 
                                 index=['Weeks Category', 'Role', 'Status'], 
                                 columns='Full Name', 
                                 aggfunc='size', 
                                 fill_value=0)

    # Check if pivot_table is not empty
    if pivot_table.empty:
        print("Pivot table is empty after filtering.")
        return

    # Reset index if needed to prepare for saving
    pivot_table = pivot_table.reset_index()

    # Save the pivot table to a CSV file
    output_file_path = os.path.join(output_dir, f'program_health_pivot_{file_name_without_extension}.csv')
    pivot_table.to_csv(output_file_path, index=True)
    print(f"Program health pivot report saved to {output_file_path}")

def plot_program_health(summary, output_dir, file_name_without_extension):
    # Ensure summary is not None and contains data
    if summary is None or summary.empty:
        print("Summary data is not available.")
        return

    # Reset index and melt the summary DataFrame
    summary = summary.reset_index().melt(id_vars='index', var_name='Role', value_name='Count')

    # Plotting logic (this is a placeholder since I don't have the full original plot code)
    print(f"Plotting data for {file_name_without_extension}")

    # Example: Saving the plot (you would replace this with actual plotting code)
    output_plot_path = os.path.join(output_dir, f'program_health_plot_{file_name_without_extension}.png')
    print(f"Program health plot saved to {output_plot_path}")

def process(input_file_path, file_name_without_extension, file_extension, output_dir):
    df = load_file(input_file_path, file_extension)
    summary = generate_program_health_report(df, output_dir, file_name_without_extension)

    generate_program_health_report(df, output_dir, file_name_without_extension)
    plot_program_health(summary,output_dir, file_name_without_extension)
    print(f'Processing User Course Summary Program Health Pivot for file: {input_file_path}')
