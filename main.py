import os
from dotenv import load_dotenv

load_dotenv()

from fetch_ccs_issue_keys import fetch_ccs_issue_keys

# Example usage:
if __name__ == "__main__":
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    data = fetch_ccs_issue_keys(jira_email, jira_api_token)
    print(data)