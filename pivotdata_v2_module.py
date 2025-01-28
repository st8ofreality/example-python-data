
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import chardet


def load_file(input_file_path, file_extension):
    if file_extension == '.xlsx':
        return pd.read_excel(input_file_path, engine='openpyxl')
    elif file_extension == '.csv':
        # Use 'chardet' to detect the file's encoding
        with open(input_file_path, 'rb') as f:
            readshortversion = chardet.detect(f.read(10000))
            encoding = readshortversion['encoding']
            
        # If encoding detection fails, fall back to 'utf-8'
        if encoding is None:
            encoding = 'utf-8'

        # Load the CSV with the detected (or fallback) encoding
        try:
            return pd.read_csv(input_file_path, encoding=encoding)
        except UnicodeDecodeError:
            # If there's still an error, force 'utf-8' encoding
            print(f"Error decoding with detected encoding ({encoding}), retrying with 'utf-8'.")
            return pd.read_csv(input_file_path, encoding='utf-8')
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

def process_dates(df):
    date_columns = ['Last Hire Date', 'Coursework Completion Date', 'Exam Completion Date', 'Mock Technical Call Completion Date']
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
            df[column] = df[column].dt.strftime('%m/%d/%Y')
    return df

def filter_and_save(df, condition, selected_fields, output_path):
    filtered_df = df[condition][selected_fields]
    filtered_df.to_csv(output_path, index=False)
    return filtered_df

def plot_completion_counts(df, groupby_fields, count_name, title, output_path):
    counts_df = df.groupby(groupby_fields).size().reset_index(name=count_name)
    plt.figure(figsize=(14, 8))
    sns.barplot(data=counts_df, x=groupby_fields[0], y=count_name, hue=groupby_fields[1])
    plt.title(title)
    plt.xlabel(groupby_fields[0])
    plt.ylabel(count_name)
    plt.xticks(rotation=45)
    plt.legend(title=groupby_fields[1])
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

def generate_spec_lists(df, output_dir, file_name_without_extension):
    df['Tickets'] = pd.to_numeric(df['Tickets'], errors='coerce')

    complete_coursework_condition = df['Coursework Status'].str.lower() == 'completed'
    selected_fields = ['Full Name', 'Job Profile', 'Region','Last Hire Date', 'Product', 'Weeks', 'Coursework Status', 'Coursework Completion Date', 'Tickets', 'Exam Status', 'Exam Completion Date', 'Mock Technical Call Status', 'Mock Technical Call Completion Date']
    
    complete_coursework_df = filter_and_save(df, complete_coursework_condition, selected_fields, f'{output_dir}/complete_coursework_{file_name_without_extension}.csv')

    qualified_tickets_condition = (
        (complete_coursework_df['Tickets'] >= 40) &
        (complete_coursework_df['Exam Status'].str.lower() != 'grandfathered') &
        (complete_coursework_df['Exam Status'].str.lower() != 'no cert') &
        (complete_coursework_df['Mock Technical Call Status'].str.lower() != 'completed')
    )
    qualified_tickets_df = filter_and_save(complete_coursework_df, qualified_tickets_condition, selected_fields, f'{output_dir}/qualified_tickets_{file_name_without_extension}.csv')

    certified_condition = (
        #(complete_coursework_df['Tickets'] >= 40) &
        (complete_coursework_df['Exam Status'].str.lower() != 'grandfathered') &
        (complete_coursework_df['Exam Status'].str.lower() != 'no cert') &
        (complete_coursework_df['Exam Status'].str.lower() == 'completed') &
        (complete_coursework_df['Mock Technical Call Status'].str.lower() == 'completed')
    )
    certified_df = filter_and_save(complete_coursework_df, certified_condition, selected_fields, f'{output_dir}/certified_{file_name_without_extension}.csv')

    coursework_completed_df = df[df['Coursework Status'] == 'Completed']
    plot_completion_counts(coursework_completed_df, ['Product', 'Job Profile'], 'Coursework Completion Count', 'Coursework Completion Count by Product and Job Profile (Completed)', f'{output_dir}/coursework_completion_count_by_product_and_job_profile_{file_name_without_extension}.png')

    exam_completed_df = df[df['Exam Status'] == 'Completed']
    plot_completion_counts(exam_completed_df, ['Product', 'Job Profile'], 'Exam Completion Count', 'Exam Completion Count by Product and Job Profile (Completed)', f'{output_dir}/exam_completion_count_by_product_and_job_profile_{file_name_without_extension}.png')

    mtc_completed_df = df[df['Mock Technical Call Status'] == 'Completed']
    plot_completion_counts(mtc_completed_df, ['Product', 'Job Profile'], 'MTC Completion Count', 'MTC Completion Count by Product and Job Profile (Completed)', f'{output_dir}/mtc_completion_count_by_product_and_job_profile_{file_name_without_extension}.png')

    print(f"Files have been saved as:\n{output_dir}/complete_coursework_{file_name_without_extension}.csv\n{output_dir}/qualified_tickets_{file_name_without_extension}.csv\n{output_dir}/certified_{file_name_without_extension}.csv")

    
def generate_stages_pivot(df, output_dir, file_name_without_extension):
    #write the statuses
    eligible_statuses = ["Completed", "In Progress", "Subscribed", "No Cert", "Grandfathered"]

    df_nocerts= df[
        (df['Product'].str.lower() != 'serverless') &
        (df['Product'].str.lower() != 'synthetics & rum') &
        (df['Product'].str.lower() != 'security')
    ]


    # Filter the rows where any of the status columns are 'Completed'
    df_filtered = df_nocerts[(df_nocerts['Coursework Status'].str.lower() == 'completed') | 
                     (df_nocerts['Exam Status'].str.lower() == 'completed') |
                     (df_nocerts['Mock Technical Call Status'].str.lower() == 'completed') 
                     ]

    # Create the pivot table
    pivot_table = pd.pivot_table(
        df_filtered,
        index=['Product', 'Coursework Status', 'Exam Status', 'Mock Technical Call Status'],  # Add eligible statuses as an additional index
        values='Full Name',  # Count of unique Full Name
        aggfunc=pd.Series.nunique,  # Count unique 'Full Name'
        fill_value=0  # Fill missing values with 0
    ).reset_index()
    
    # Rename "Full Name" column to "Count"
    pivot_table.rename(columns={'Full Name': 'Count'}, inplace=True)

    # Save the pivot table to a CSV file
    output_file_path = os.path.join(output_dir, f'stages_pivot_{file_name_without_extension}.csv')
    pivot_table.to_csv(output_file_path, index=False)
    print(f"Stages pivot report saved to {output_file_path}")

def generate_stuck_phases_pivot(df, output_dir, file_name_without_extension):
    # Step 1: Create the 'Weeks Category' column based on 'Adjusted Weeks'
    df['Weeks Category'] = ['<= 16' if x <= 16 else '> 16' for x in df['Weeks']]

    # Step 2: Filter to exclude specific products
    df_filtered = df[
        (df['Product'].str.lower() != 'serverless') &
        (df['Product'].str.lower() != 'synthetics & rum') &
        (df['Product'].str.lower() != 'security')
    ]

    # Step 3: Melt the DataFrame to long format based on 'Weeks Category' and 'Product'
    df_melted = df_filtered.melt(
        id_vars=['Full Name', 'Product', 'Weeks Category','Tickets' ], 
        value_vars=['Coursework Status', 'Exam Status', 'Mock Technical Call Status'], 
        var_name='Phase', 
        value_name='Status'
    )

    dfmelt_output = os.path.join(output_dir, f'dfmelt_{file_name_without_extension}.csv')
    df_melted.to_csv(dfmelt_output, index=False)

    # Step 4: Group the data for dependent filtering
    grouped = df_melted.groupby(['Full Name', 'Product', 'Weeks Category'])

    # Step 5: Define functions to identify stuck phases
    def is_stuck_at_exam_course(group):
        coursework_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                (group['Status'].str.lower() == 'completed')).any() 
        exam_not_completed = ((group['Phase'].str.lower() == 'exam status') & 
                              (group['Status'].str.lower() != 'completed') & 
                              (group['Status'].str.lower() != 'grandfathered')).any()
                              #& (group['Status'].str.lower() != 'not enrolled')).any()
        return coursework_completed and exam_not_completed

    def is_stuck_at_cert(group):
        coursework_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                (group['Status'].str.lower() == 'completed')).any()
        exam_completed = ((group['Phase'].str.lower() == 'exam status') & 
                          (group['Status'].str.lower() == 'completed')).any()
        cert_not_completed = ((group['Phase'].str.lower() == 'mock technical call status') & 
                              (group['Status'].str.lower() != 'completed') & 
                              (group['Status'].str.lower() != 'grandfathered') & 
                              (group['Status'].str.lower() != 'not enrolled')).any()
        return coursework_completed and exam_completed and cert_not_completed

    def is_stuck_at_cert_more_than_40(group):
        coursework_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                (group['Status'].str.lower() == 'completed')).any()
        exam_completed = ((group['Phase'].str.lower() == 'exam status') & 
                          (group['Status'].str.lower() == 'completed')).any()
        cert_not_completed = ((group['Phase'].str.lower() == 'mock technical call status') & 
                              (group['Status'].str.lower() != 'completed') & 
                              (group['Status'].str.lower() != 'grandfathered') & 
                              (group['Status'].str.lower() != 'not enrolled')).any()
        more_than_40_tickets = (group['Tickets'] >= 40).all()
        return coursework_completed and exam_completed and cert_not_completed
    
    def is_stuck_at_cert_less_than_40(group):
        coursework_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                (group['Status'].str.lower() == 'completed')).any()
        exam_completed = ((group['Phase'].str.lower() == 'exam status') & 
                          (group['Status'].str.lower() == 'completed')).any()
        cert_not_completed = ((group['Phase'].str.lower() == 'mock technical call status') & 
                              (group['Status'].str.lower() != 'completed') & 
                              (group['Status'].str.lower() != 'grandfathered') & 
                              (group['Status'].str.lower() != 'not enrolled')).any()
        less_than_40_tickets = (group['Tickets'] < 40).all()
        return coursework_completed and exam_completed and cert_not_completed

    def is_stuck_at_coursework(group):
        coursework_not_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                    (group['Status'].str.lower() != 'completed') &
                                    (group['Status'].str.lower() != 'not enrolled')).any()
        return coursework_not_completed
    
    def coursework_completed(group):
        coursework_completed = ((group['Phase'].str.lower() == 'coursework status') & 
                                    (group['Status'].str.lower() == 'completed')).any()
        return coursework_completed

    # Step 6: Apply conditions to each group
    stuck_at_coursework_df = grouped.filter(is_stuck_at_coursework)
    stuck_at_exam_df = grouped.filter(is_stuck_at_exam_course)
    stuck_at_cert__more_than_40_df = grouped.filter(is_stuck_at_cert_more_than_40)
    stuck_at_cert_less_than_40_df = grouped.filter(is_stuck_at_cert_less_than_40)
    stuck_at_cert_df = grouped.filter(is_stuck_at_cert)
    coursework_completed = grouped.filter(coursework_completed)


    # Step 7: Create pivot tables to count unique 'Full Name' for each phase by 'Product'
    stuck_at_coursework_pivot = pd.pivot_table(
        stuck_at_coursework_df,
        index=['Weeks Category', 'Product'], # Grouping by Product and Weeks Category
        values='Full Name',
        aggfunc=pd.Series.nunique,
        fill_value=0
    ).reset_index()
    
    stuck_at_coursework_pivot.rename(columns={'Full Name': 'Stuck at Coursework'}, inplace=True)

    stuck_at_exam_pivot = pd.pivot_table(
        stuck_at_exam_df,
        index=['Weeks Category', 'Product'], # Grouping by Product and Weeks Category
        values='Full Name',
        aggfunc=pd.Series.nunique,
        fill_value=0
    ).reset_index()
    stuck_at_exam_pivot.rename(columns={'Full Name': 'Stuck at Exam Course'}, inplace=True)

    stuck_at_cert_pivot = pd.pivot_table(
        stuck_at_cert_df,
        index=['Weeks Category', 'Product'], # Grouping by Product and Weeks Category
        values='Full Name',
        aggfunc=pd.Series.nunique,
        fill_value=0
    ).reset_index()
    stuck_at_cert_pivot.rename(columns={'Full Name': 'Stuck at Cert'}, inplace=True)



    # Step 8: Add new columns based on Status, Tickets >40 and Tickets <40
    # Step 8.1: Count of people "Enrolled" for that product
    enrolled_pivot= df_melted[
        (df_melted['Status'].str.lower() != 'not enrolled') &
        (df_melted['Phase'].str.lower() == 'coursework status') 
         ].groupby(['Weeks Category', 'Product']).agg({'Full Name' : pd.Series.nunique}).reset_index().rename(columns={'Full Name': 'Enrolled'})

    # Step 8.2: Count of people with Tickets for columns
    cert_tickets_greater_than_equal_40_pivot = df_melted[
        (df_melted['Tickets']>= 40) & 
        ((df_melted['Phase'].str.lower()=='coursework status') & (df_melted['Status'].str.lower()=='completed'))
         ].groupby(['Weeks Category', 'Product']).agg({'Full Name': pd.Series.nunique}).reset_index().rename(columns={'Full Name' : 'At Cert with Tickets >= 40'})
    cert_tickets_less_than_40_pivot = df_melted[
        (df_melted['Tickets'] < 40) & 
        ((df_melted['Phase'].str.lower()=='coursework status') & (df_melted['Status'].str.lower()=='completed'))
        ].groupby(['Weeks Category','Product']).agg({'Full Name': pd.Series.nunique}).reset_index().rename(columns={'Full Name':'At Cert with Tickets < 40'})

    # Step 9: Compare "Stuck at Cert" and "Tickets > 40"
    # Step 9.1: Count of people with Tickets for matching   
    tickets_greater_than_equal_40_pivot = df_melted[df_melted['Tickets']>= 40].groupby([ 'Weeks Category', 'Product']).agg({'Full Name': pd.Series.nunique}).reset_index().rename(columns={'Full Name' : 'Tickets > 40'})
    tickets_less_than_40_pivot = df_melted[df_melted['Tickets']< 40].groupby([ 'Weeks Category','Product']).agg({'Full Name': pd.Series.nunique}).reset_index().rename(columns={'Full Name':'Tickets <= 40'})

    # Step 9.2: Drop dupes
    stuck_at_cert_names = stuck_at_cert_df[['Full Name', 'Weeks Category', 'Product', 'Tickets']].drop_duplicates()
    tickets_gt_40_names = df_melted[df_melted['Tickets'] >= 40][['Full Name', 'Weeks Category', 'Product', 'Tickets']].drop_duplicates()


    # Step 9.3: Perform an inner join to find names that are in both datasets
    match_df = pd.merge(stuck_at_cert_names, tickets_gt_40_names, on=['Full Name', 'Weeks Category', 'Product'], how='inner', suffixes=('_stuck_cert', '_tickets_gt_40'))

    # Step 9.4: Count the matches by 'Weeks Category' and 'Product' and output csv
    match_count_pivot = match_df.groupby(['Weeks Category', 'Product']).agg({'Full Name': pd.Series.nunique}).reset_index()
    names_output_file_path = os.path.join(output_dir, f'overlapping_names_{file_name_without_extension}.csv')
    match_df.to_csv(names_output_file_path, index=False)

    # Step 10: Merge the pivot tables into one
    final_pivot = pd.merge(stuck_at_coursework_pivot, stuck_at_exam_pivot, on=['Weeks Category', 'Product'], how='outer')
    final_pivot = pd.merge(final_pivot, cert_tickets_greater_than_equal_40_pivot, on=['Weeks Category', 'Product'], how='outer')
    final_pivot = pd.merge(final_pivot, cert_tickets_less_than_40_pivot, on=['Weeks Category', 'Product'], how='outer')
    final_pivot = pd.merge(final_pivot, enrolled_pivot, on=['Weeks Category', 'Product'], how='outer')

    # Step 11: Replace NaN values with 0 (in case some products do not have counts for all phases)
    final_pivot.fillna(0, inplace=True)

    # Step 12: Save the final pivot table to a CSV file
    output_file_path = os.path.join(output_dir, f'stuck_phases_pivot_{file_name_without_extension}.csv')
    final_pivot.to_csv(output_file_path, index=False)
    print(f"Stuck phases pivot report with Weeks Category saved to {output_file_path}")


def process(input_file_path, file_name_without_extension, file_extension, output_dir):
    df = load_file(input_file_path, file_extension)  # Directly load the input file
    
    generate_spec_lists(df, output_dir, file_name_without_extension)
    generate_stages_pivot(df, output_dir, file_name_without_extension)
    generate_stuck_phases_pivot(df, output_dir, file_name_without_extension)