import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

def fetch_ccs_issue_keys(jira_email: str, jira_api_token: str, base_url: str = "https://contentful.atlassian.net"):
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
    payload = {
        "jql": "project = CCS AND status in ('New Idea','Clarifying with Field','On Hold')",
        "fields": ["key"]
    }

    response = requests.post(url, auth=auth, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Example usage:
if __name__ == "__main__":
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    data = fetch_ccs_issue_keys(jira_email, jira_api_token)
    print(data)