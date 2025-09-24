import os
from dotenv import load_dotenv

load_dotenv()

from fetch_ccs_issue_keys import fetch_ccs_issue_keys
from fetch_ccs_issue_details import fetch_ccs_issue_details



# Example usage:
if __name__ == "__main__":
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    keys = fetch_ccs_issue_keys(jira_email, jira_api_token)
    data = fetch_ccs_issue_details(jira_email, jira_api_token, keys, aws_access_key_id, aws_secret_access_key)