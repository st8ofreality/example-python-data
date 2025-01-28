import os
import pandas as pd
import requests
import time
import sys
import json

def load_file(input_file_path, file_extension):
    if file_extension == '.json':
        with open(input_file_path, 'r') as f:
            return pd.json_normalize(json.load(f))
    else:
        raise ValueError("TRAINING LMS API Report requires a .json file.")


def get_api_token():
    """Capture API Token from OS environment variable."""
    api_token = os.getenv('TRAINING_API_TOKEN')
    if not api_token:
        raise EnvironmentError("API token not found in environment variables. Please set the TRAINING_API_TOKEN environment variable.")
    return api_token

#%%
def export_report(api_token, report_id):
    """Initiate report export and retrieve execution_id."""
    url = f'{API_URL}/{report_id}/export/csv'
    #url = f'{API_URL}/{report_id}/export/xlsx'

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {api_token}", 
        "content-type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    # debug api request with prints
    # print(f'URL: {response.url}')
    # print(f'Status Code: {response.status_code}')
    # print(f'Headers: {response.request.headers}')
    # print(f'Response: {response.text}')
    response.raise_for_status()

    
    json_response = response.json()
    execution_id = json_response['data']['executionId']
    print(f'Execution ID: {execution_id}')
    return execution_id

#%%
def check_report_status(api_token, report_id, execution_id):
    """Check the status of the report export until it is completed."""
    url = f'{API_URL}/{report_id}/exports/{execution_id}'
    headers = {
        "Authorization": f"Bearer {api_token}", 
        "Content-Type": "application/json"
    }    
    while True:
        response = requests.get(url, headers=headers)
        #debug api request with prints
        # print(f'URL: {response.url}')
        # print(f'Status Code: {response.status_code}')
        # print(f'Headers: {response.request.headers}')
        # print(f'Response: {response.text}')
        response.raise_for_status()
        
        json_response = response.json()
        status = json_response['data']['status']
        
        if status == 'SUCCEEDED':
            break
        elif status == 'FAILED':
            raise Exception('Report export failed.')
        
        time.sleep(15)  # Wait for 15 seconds before retrying
        print("Checking status...")

#%%
def download_report(api_token, report_id, execution_id, output_path):
    """Download the exported report file to the specified filepath."""
    url = f'{API_URL}/{report_id}/exports/{execution_id}/download'
    headers = {
        "Authorization": f"Bearer {api_token}", 
        "Content-Type": "application/json"
    }    
    response = requests.get(url, headers=headers)
    # debug api request with prints
    # print(f'URL: {response.url}')
    # print(f'Status Code: {response.status_code}')
    # print(f'Headers: {response.request.headers}')
    # print(f'Response: {response.text}')
    response.raise_for_status()
    
    with open(output_path, 'wb') as file:
        file.write(response.content)
    print(f'File downloaded to {output_path}')


def process(input_file_path, file_extension, report_output_dir):    
    df = load_file(input_file_path, file_extension)
    print(f'Processing TRAINING LMS API Report for file: {input_file_path}')
    
    # Capture API token from OS environment variable
    try: 
        api_token = get_api_token()
    except EnvironmentError as e:
        print(e)
        sys.exit(1)

    #Read config file from the specified path  
    with open(input_file_path, 'r') as config_file: 
        config =json.load(config_file)


    for report in config['reports']:
        report_id = report['report_id']
        filename = report['filename']
        output_path= os.path.join(report_output_dir, filename)

        try:
            # Step 1: Make API call to export the report
            print('Exporting report...')
            execution_id = export_report(api_token, report_id)
            
            # Step 2: Check the status of the report export until it is completed
            print('Checking report status...')
            check_report_status(api_token, report_id, execution_id)

            # Step 3: Download the report file once the status is completed
            print('Downloading report...')
            download_report(api_token, report_id, execution_id, output_path)
            print('Report download completed.')
        
        except requests.RequestException as e:
            print(f'Error occurred: {e}')
            sys.exit(1)
        
        
