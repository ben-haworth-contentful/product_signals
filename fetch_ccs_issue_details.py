import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import os
import boto3
from botocore.exceptions import NoCredentialsError

def upload_directory_to_s3(directory_path: str, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region_name: str = "eu-central-1"):
    """
    Uploads the specified directory to an S3 bucket.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.relpath(file_path, os.path.dirname(directory_path))
            try:
                s3_client.upload_file(file_path, bucket_name, f"{os.path.basename(directory_path)}/{s3_key}")
                print(f"Uploaded {file_path} to s3://{bucket_name}/{os.path.basename(directory_path)}/{s3_key}")
            except FileNotFoundError:
                print(f"The file {file_path} was not found.")
            except NoCredentialsError:
                print("Credentials not available.")

def fetch_ccs_issue_details(jira_email: str, jira_api_token: str, keys: list[str], aws_access_key_id: str, aws_secret_access_key: str, base_url: str = "https://contentful.atlassian.net"):
    """
    Fetch all issue keys in project CCS with status New Idea, Clarifying with Field, or On Hold.

    Returns the JSON response from the /search/jql endpoint.
    """
    url = f"{base_url}/rest/api/3/search/jql"
    auth = HTTPBasicAuth(jira_email, jira_api_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime("%Y-%m-%d")
    directory_path = f"raw/jira/CCS/{current_date}"
    
    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    for key in keys:
        payload = {
            "jql": f"project = CCS AND issueKey in ({key})",
            "fields": ["*all"]
        }

        print("Request payload:", json.dumps(payload, indent=2))

        resp = requests.post(url, auth=auth, headers=headers, json=payload)

        data = resp.json()

        print(data)

        # Write the response to a JSON file in the dated directory
        file_path = f"{directory_path}/{key}.json"
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    # Upload the directory to S3
    upload_directory_to_s3(directory_path, 'product-signals', aws_access_key_id, aws_secret_access_key)