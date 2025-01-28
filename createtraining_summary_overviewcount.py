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

def generate_program_overview_report(df, output_dir, file_name_without_extension):
    status_columns = ['NHO', 'Agent', 'Spec 1', 'Spec 2', 'Spec 3']
    statuses = ["Completed", "On Track", "Working On Tickets", "Training Behind", "Certification Behind", "Not Started"]
    
    # Initialize the summary dataframe
    summary = pd.DataFrame(index=statuses, columns=['Total'] + status_columns)
    summary = summary.fillna(0).infer_objects(copy=False)    
    
    # Calculate the counts
    for status in statuses:
        if status == "Not Started":
            df['NHO'] = df['NHO'].replace('Not Started', 'N/A')
        summary.at[status, 'Total'] = (df[status_columns] == status).sum().sum()
        for col in status_columns:
            summary.at[status, col] = (df[col] == status).sum()
    
    # Add the total row
    total_row = summary.sum(numeric_only=True)
    total_row.name = 'Total'
    
    # Adjust the 'Total' column for the total row to match the count of unique names
    total_row['Total'] = df['Full Name'].nunique()
    
    # Concatenate the total row to the summary dataframe
    summary = pd.concat([summary, total_row.to_frame().T])
    
    # Save the summary to a CSV file
    output_file_path = os.path.join(output_dir, f'program_health_{file_name_without_extension}.csv')
    summary.to_csv(output_file_path, index=True)
    print(f"Program health report saved to {output_file_path}")

    return summary

def plot_program_overview(summary, output_dir, file_name_without_extension):
    summary = summary.reset_index().melt(id_vars='index', var_name='Role', value_name='Count')
    summary = summary[summary['index'] != 'Total']  # Exclude the total row from the plot
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=summary, x='Role', y='Count', hue='index')
    plt.title('Program Health Summary')
    plt.xlabel('Role')
    plt.ylabel('Count')
    plt.legend(title='Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plot_file_path = os.path.join(output_dir, f'program_health_summary_{file_name_without_extension}.png')
    plt.savefig(plot_file_path, dpi=300)
    print(f"Program health summary plot saved to {plot_file_path}")
    #plt.show()


def process(input_file_path, file_name_without_extension, file_extension, output_dir):
    df = load_file(input_file_path, file_extension)
    summary = generate_program_overview_report(df, output_dir, file_name_without_extension)

    generate_program_overview_report(df, output_dir, file_name_without_extension)
    plot_program_overview(summary, output_dir, file_name_without_extension)
    print(f'Processing Summary Program Overview for file: {input_file_path}')
