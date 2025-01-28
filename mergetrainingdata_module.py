
import pandas as pd
import os
import chardet

# Load file function as provided
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


def filter_and_merge(user_course_data, tm_data, product_mapping):
    # Ensure Email and Username are in the same format (lowercase, stripped of spaces)
    user_course_data['Email'] = user_course_data['Email'].str.strip().str.lower()
    tm_data['Username'] = tm_data['Username'].str.strip().str.lower()

    # Ensure Product and Training Material Title match correctly
    user_course_data['Product'] = user_course_data['Product'].str.strip()
    tm_data['Training Material Title'] = tm_data['Training Material Title'].str.strip()

    # Create empty columns for the final output
    user_course_data['Exam Training Material Score'] = None
    user_course_data['Exam Training Material Status'] = None
    user_course_data['Exam Training Material Completion Date'] = None
    user_course_data['Readiness Check Status'] = None
    user_course_data['Readiness Check Last Completion Date'] = None

    # Iterate through each product and apply the mapping

def merge_user_course_and_tm_reports(input_file1_path,file1_extension, input_file2_path,file2_extension):
    # Load datasets
    tm_data = load_file(input_file1_path,file1_extension)
    user_course_data = load_file(input_file2_path,file2_extension)

    
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
    
    # Filter and merge data
    merged_data = filter_and_merge(user_course_data, tm_data, product_mapping)
    
    return merged_data

def process(input_file1_path, file1_extension, input_file2_path, file2_extension, output_dir):
    # Call the merge function and get the merged dataframe
    merged_data = merge_user_course_and_tm_reports(input_file1_path,file1_extension, input_file2_path,file2_extension)
    
    # Output the merged data to the output_dir
    output_file = os.path.join(output_dir, 'merged_spec_tm_report.csv')
    merged_data.to_csv(output_file, index=False)
    print(f"Merged report saved successfully to {output_file}")