import requests
from requests.auth import HTTPBasicAuth
import json

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
        "jql": "project = CCS AND status in ('New Idea','Clarifying with Field','On Hold')",
        "fields": ["key"],
        "maxResults": max_results
    }

    is_last = False
    page_token = None
    all_keys = []
    iteration = 1

    while not is_last and iteration < 100:
           
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
