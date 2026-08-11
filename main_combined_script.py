
import os
import program_health_script_v6
import createtraining_summary_overviewcount
import api_report_config
import api_obschecklist_config
import pivotdata_v2_module
import merge_trainingdataog
import mergetrainingdata_module

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


def main():
    print("Select the scripts to run (comma-separated numbers for multiple selections):")
    print("1. Program Health Script V6")
    print("2. Summary Program Overview")
    print("3. LMS API Report (.json required)")
    print("4. LMS API Observation Checklist (.json required)")
    print("5. Product Spec V2")
    
    choices = input("Enter your choices: ").split(',')

    # For each choice, get the appropriate file path
    for choice in choices:
        choice = choice.strip()

        if choice == '1':
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('Program Health Script V6')
            program_health_script_v6.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        elif choice == '2':
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('Summary Program Health')
            createtraining_summary_overviewcount.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        elif choice == '3':
            _, input_file_path, _, file_extension, _, report_output_dir, _ = get_file_paths('LMS API Report')
            api_report_config.process(input_file_path, file_extension, report_output_dir)
        elif choice == '4':
            _, input_file_path, _, file_extension, _, _, checklist_output_dir = get_file_paths('LMS API Observation Checklist')
            api_obschecklist_config.process(input_file_path, file_extension, checklist_output_dir)
        elif choice == '5':
            _, input_file_path, file_name_without_extension, file_extension, output_dir, _, _ = get_file_paths('Product Spec V2')
            pivotdata_v2_module.process(input_file_path, file_name_without_extension, file_extension, output_dir)
        else:
            print(f"Invalid choice: {choice}")

if __name__ == "__main__":
    main()
