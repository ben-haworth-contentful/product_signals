import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv()

def fetch_ccs_issue_keys(jira_email: str, jira_api_token: str, base_url: str = "https://contentful.atlassian.net", max_results: int = 100):
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
    
    # Initial payload
    payload_template = {
        #"jql": "project = CCS AND status in ('New Idea','Clarifying with Field','On Hold')",
        "jql": "project = CCS",
        "fields": ["key"],
        "maxResults": max_results
    }

    is_last = False
    page_token = None
    all_keys = []
    iteration = 1

    while not is_last and iteration <= 100:
           
        if page_token:
            payload = payload_template
            payload["nextPageToken"] = page_token
        else:
            payload = payload_template

        print(f"\n=== Iteration {iteration} ===")
        print("Request payload:", json.dumps(payload, indent=2))

        resp = requests.post(url, auth=auth, headers=headers, json=payload)

        data = resp.json()

        issues = data.get("issues", [])
        if not issues:
            break

        for issue in issues:
            all_keys.append(issue["key"])

        print(f"Returned {len(issues)} issues this page")
        print(f"Returned {len(all_keys)} issues in total")
        print("Response nextPageToken:", data.get("nextPageToken"))
        print("Response isLast:", data.get("isLast"))

        # Check pagination
        page_token = data.get("nextPageToken")
        is_last = data.get("isLast")
        iteration += 1

    return all_keys


def upload_directory_to_s3(directory_path: str, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region_name: str = "eu-central-1"):
    """
    Uploads the specified directory to an S3 bucket.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Construct the S3 key to include the full path from the 'raw' directory
            s3_key = os.path.relpath(file_path)
            try:
                s3_client.upload_file(file_path, bucket_name, s3_key)
                print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
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

# Example usage:
if __name__ == "__main__":

    # Get the environment variables
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Get the issue keys
    keys = fetch_ccs_issue_keys(jira_email, jira_api_token)
    
    # Fetch the issue details and write them to S3
    fetch_ccs_issue_details(jira_email, jira_api_token, keys, aws_access_key_id, aws_secret_access_key)