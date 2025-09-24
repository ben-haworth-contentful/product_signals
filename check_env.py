import os
from dotenv import load_dotenv
load_dotenv()

print("JIRA_API_TOKEN is:", os.getenv("JIRA_API_TOKEN"))