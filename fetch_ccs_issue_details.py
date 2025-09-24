import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import os

def fetch_ccs_issue_details(jira_email: str, jira_api_token: str, keys: list[str], base_url: str = "https://contentful.atlassian.net"):
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