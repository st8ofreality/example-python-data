import requests
import json
import os
import pandas as pd
import time

def load_file(input_file_path, file_extension):
    if file_extension == '.json':
        with open(input_file_path, 'r') as f:
            return pd.json_normalize(json.load(f))
    else:
        raise ValueError("Training API Observation Checklist requires a .json file.")


def get_api_token():
    """Capture API Token from OS environment variable."""
    api_token = os.getenv('TRAINING_API_TOKEN')
    if not api_token:
        raise EnvironmentError("API token not found in environment variables. Please set the TRAINING_API_TOKEN environment variable.")
    return api_token

def get_api_url():
    """Capture API Base URL from OS environment variable."""
    return os.getenv('TRAINING_API_URL', 'https://api.example.com')

def fetch_checklist_data(api_token, checklist_id):
    """Fetch checklist data from the Training LMS API."""
    api_url = get_api_url()
    url = f"{api_url}/checklists/{checklist_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json['data']['items']
        except requests.RequestException as e:
            print(f'Attempt {attempt + 1} failed: {e}')
            time.sleep(2)
    raise Exception("Failed to fetch checklist data after 3 attempts")

def process_checklists(config, api_token,checklist_output_dir):
    """Process each checklist and combine data based on the output file specified in the config."""
    all_dataframes = {}

    for checklist in config['checklists']:
        print(f'Processing checklist: {checklist}')  # Debugging print statement
        checklist_id = checklist['checklist_id']
        checklist_name = checklist['checklist_name']
        output_file = checklist['output_file']
        
        print(f'Fetching data for checklist {checklist_id}...')
        items = fetch_checklist_data(api_token, checklist_id)
        df = pd.json_normalize(items)
        df['checklist_name'] = checklist_name

        if output_file not in all_dataframes:
            all_dataframes[output_file] = []
        all_dataframes[output_file].append(df)
    

    for output_file, dataframes in all_dataframes.items():
        combined_df = pd.concat(dataframes, ignore_index=True)
        output_path = f'{checklist_output_dir}/{output_file}'
        combined_df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")

   

def process(input_file_path, file_extension, checklist_output_dir):
    df = load_file(input_file_path, file_extension)

    try: 
        api_token = get_api_token()
    except EnvironmentError as e:
        print(e)
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        config = json.load(file)

    process_checklists(config, api_token, checklist_output_dir)
    print(f'Processing Training LMS API Observation Checklist for file: {input_file_path}')
