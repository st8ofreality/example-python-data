import os
import program_health_script_v6
import createtraining_summary_overviewcount
import api_report_config
import api_obschecklist_config
import pivotdata_v2_module
import merge_trainingdataog
import mergetrainingdata_module # Import the merge module

# Get file paths function as before
def get_file_paths(operation):
    username = os.getlogin()
    python_path = f'/Users/{username}/python'
    input_file = input(f'Enter a file name for {operation} (.csv, .xlsx, or .json): ')
    file_name_without_extension, file_extension = os.path.splitext(input_file)
    input_file_path = os.path.expanduser(f'{python_path}/inputs/{input_file}')
    output_dir = os.path.expanduser(f'{python_path}/outputs')
    os.makedirs(output_dir, exist_ok=True)
    report_output_dir = os.path.expanduser(f'{python_path}/reports')
    os.makedirs(report_output_dir, exist_ok=True)
    checklist_output_dir = os.path.expanduser(f'{python_path}/checklists')
    os.makedirs(checklist_output_dir, exist_ok=True)
    return python_path, input_file_path, file_name_without_extension, file_extension, output_dir, report_output_dir, checklist_output_dir

# New function to get dual file paths for merging Spec and TM reports
def get_dual_paths(operation):
    username = os.getlogin()
    python_path = f'/Users/{username}/python'
    
    # Prompt explicitly for TM data and Spec data
    input_file1 = input(f'Enter the TM data file name for {operation} (.csv or .xlsx): ')
    file1_name_without_extension, file1_extension = os.path.splitext(input_file1)
    input_file1_path = os.path.expanduser(f'{python_path}/inputs/{input_file1}')
    
    input_file2 = input(f'Enter the Spec data file name for {operation} (.csv or .xlsx): ')
    file2_name_without_extension, file2_extension = os.path.splitext(input_file2)
    input_file2_path = os.path.expanduser(f'{python_path}/inputs/{input_file2}')
    
    output_dir = os.path.expanduser(f'{python_path}/outputs')
    os.makedirs(output_dir, exist_ok=True)

    return input_file1_path, file1_extension, input_file2_path, file2_extension, output_dir

# Main function handling user choices
def main():
    print("Select the scripts to run (comma-separated numbers for multiple selections):")
    print("1. Program Health Script V6")
    print("2. GSE Summary Program Overview")
    print("3. Docebo API Report (.json required)")
    print("4. Docebo API Observation Checklist (.json required)")
    print("5. GSE Product Spec V2")
    print("6. Merge Spec and TM reports")
    
    choices = input("Enter your choices: ").split(',')

    # For each choice, get the appropriate file path
    for choice in choices:
        choice = choice.strip()

        if choice == '1':
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('Program Health Script V6')
            program_health_script_v6.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        elif choice == '2':
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('GSE Summary Program Health')
            createtraining_summary_overviewcount.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        elif choice == '3':
            _, input_file_path, _, file_extension, _, report_output_dir, _ = get_file_paths('Docebo API Report')
            api_report_config.process(input_file_path, file_extension, report_output_dir)
        elif choice == '4':
            _, input_file_path, _, file_extension, _, _, checklist_output_dir = get_file_paths('Docebo API Observation Checklist')
            api_obschecklist_config.process(input_file_path, file_extension, checklist_output_dir)
        elif choice == '5':
            # Handle GSE Product Spec V2
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('GSE Product Spec V2')
            pivotdata_v2_module.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        elif choice == '6':
            # Using get_dual_paths to handle merging Spec and TM reports
            input_file1_path, file1_extension, input_file2_path, file2_extension, output_dir = get_dual_paths('Merge Spec and TM reports')
            mergetrainingdata_module.process(input_file1_path, file1_extension, input_file2_path, file2_extension, output_dir)
        else:
            print(f"Invalid choice: {choice}")

if __name__ == "__main__":
    main()