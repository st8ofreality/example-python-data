import pandas as pd
import os
import chardet

# Load file function to handle .xlsx and .csv formats
def load_file(input_file_path, file_extension):
    print(f"Loading file: {input_file_path} with extension: {file_extension}")
    if file_extension == '.xlsx':
        return pd.read_excel(input_file_path, engine='openpyxl')
    elif file_extension == '.csv':
        # Detect the file's encoding using 'chardet'
        with open(input_file_path, 'rb') as f:
            readshortversion = chardet.detect(f.read(10000))
            encoding = readshortversion['encoding']
        
        if encoding is None:
            encoding = 'utf-8'

        # Load the CSV file with detected or fallback encoding
        try:
            return pd.read_csv(input_file_path, encoding=encoding)
        except UnicodeDecodeError:
            print(f"Error decoding with detected encoding ({encoding}), retrying with 'utf-8'.")
            return pd.read_csv(input_file_path, encoding='utf-8')
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

# Groupby function for TM data
def group_tm_data(tm_data):
    print("Grouping TM data by 'Username' and 'Training Material Title'...")
    grouped_tm = tm_data.groupby(['Username', 'Training Material Title']).agg({
        'Training Material Score': 'first',
        'Training Material Status': 'first',
        'Training Material Last Completion Date': 'first'
    }).reset_index()
    
    if grouped_tm.empty:
        print("Warning: No data found after grouping TM data.")
    
    return grouped_tm

# Merge user course data with grouped TM data
def merge_with_usercoursedata(user_course_data, grouped_tm_data, product_mapping):
    # Ensure Email and Username are in the same format (lowercase, stripped of spaces)
    user_course_data['Email'] = user_course_data['Email'].str.strip().str.lower()
    grouped_tm_data['Username'] = grouped_tm_data['Username'].str.strip().str.lower()
    grouped_tm_data['Training Material Title'] = grouped_tm_data['Training Material Title'].str.strip()

    # Create empty columns for Exam and Readiness Check data
    user_course_data['Exam Training Material Score'] = None
    user_course_data['Exam Training Material Status'] = None
    user_course_data['Exam Training Material Completion Date'] = None
    user_course_data['Readiness Check Status'] = None
    user_course_data['Readiness Check Last Completion Date'] = None

    # Iterate through each product and apply the mapping
    for product, materials in product_mapping.items():
        certification_exam, readiness_check = materials

        # Merge Exam-related data
        exam_data = grouped_tm_data[grouped_tm_data['Training Material Title'] == certification_exam]
        if exam_data.empty:
            print(f"Warning: No exam data found for product {product}.")

        user_course_data = user_course_data.merge(
            exam_data[['Username', 'Training Material Score', 'Training Material Status', 'Training Material Last Completion Date']],
            left_on=['Email'], right_on=['Username'], how='left', suffixes=('', '_exam')
        )

        # Assign Exam columns
        user_course_data['Exam Training Material Score'] = user_course_data['Training Material Score']
        user_course_data['Exam Training Material Status'] = user_course_data['Training Material Status']
        user_course_data['Exam Training Material Completion Date'] = user_course_data['Training Material Last Completion Date']

        # Drop temporary columns from the merge
        user_course_data = user_course_data.drop(columns=['Username', 'Training Material Score', 'Training Material Status', 'Training Material Last Completion Date'])

        # Merge Readiness Check-related data
        readiness_data = grouped_tm_data[grouped_tm_data['Training Material Title'] == readiness_check]
        if readiness_data.empty:
            print(f"Warning: No readiness check data found for product {product}.")

        user_course_data = user_course_data.merge(
            readiness_data[['Username', 'Training Material Status', 'Training Material Last Completion Date']],
            left_on=['Email'], right_on=['Username'], how='left', suffixes=('', '_readiness')
        )

        # Assign Readiness Check columns
        user_course_data['Readiness Check Status'] = user_course_data['Training Material Status_readiness']
        user_course_data['Readiness Check Last Completion Date'] = user_course_data['Training Material Last Completion Date_readiness']

        # Drop temporary columns from the merge
        user_course_data = user_course_data.drop(columns=['Username', 'Training Material Status_readiness', 'Training Material Last Completion Date_readiness'])

    if user_course_data.empty:
        print("Error: No data available in uploaded data after merging.")
        return None
    
    return user_course_data

# Updated process function with dual inputs
def process(input_file1_path, file1_extension, input_file2_path, file2_extension, output_dir):
    # Load both files (users course report and training material)
    user_course_data = load_file(input_file1_path, file1_extension)
    tm_data = load_file(input_file2_path, file2_extension)

    # Check if the data is loaded successfully
    if user_course_data is None or tm_data is None:
        print("Error loading one or both files. Please check the file paths.")
        return None

    print(f"User Course Data: {len(user_course_data)} rows loaded.")
    print(f"TM Data: {len(tm_data)} rows loaded.")

    # Group TM data by Username and Training Material Title
    grouped_tm_data = group_tm_data(tm_data)

    # Product to Training Material Mapping
    product_mapping = {
        'Product 1': ['Product 1 Certification Exam', 'Product 1 Certification Readiness Check'],
        'Product 2': ['Product 2 Certification Exam', 'Product 2 Certification Readiness Check'],
        'Product 3': ['Product 3 Certification Exam', 'Product 3 Certification Readiness Check'],
        'Product 4': ['Product 4 Certification Exam', 'Product 4 Certification Readiness Check'],
        'Product 5': ['Product 5 Certification Exam', 'Product 5 Certification Readiness Check'],
        'Product 6': ['Product 6 Certification Exam', 'Product 6 Certification Readiness Check'],
        'Product 7': ['Product 7 Certification Exam', 'Product 7 Certification Readiness Check'],
        'Product 8': ['Product 8 Certification Exam', 'Product 8 Certification Readiness Check']
    }

    # Merge grouped TM data with User Course data
    merged_data = merge_with_usercoursedata(user_course_data, grouped_tm_data, product_mapping)

    if merged_data is not None:
        output_file = os.path.join(output_dir, 'merged_tm_report.csv')
        merged_data.to_csv(output_file, index=False)
        print(f"Merged report saved to {output_file}")
    else:
        print("No data to save. No matches were found.")

    return merged_data