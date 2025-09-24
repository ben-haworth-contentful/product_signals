#!/usr/bin/env python3
import os
import boto3
from datetime import datetime
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

# S3 configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'jira-data')  # Default bucket name
S3_CLIENT = boto3.client('s3')

def upload_issue_to_s3(local_file_path, issue_key):
    """
    Upload a single issue JSON file to S3 with the specified path format:
    s3://jira-data/raw/CCS/yyyy-MM-dd/CCS-3023.json
    """
    # Get current date in yyyy-MM-dd format
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Construct S3 key (path) following the specified format
    s3_key = f"raw/CCS/{date_str}/{issue_key}.json"
    
    try:
        # Upload file to S3
        S3_CLIENT.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)
        print(f"✅ Uploaded {issue_key} → s3://{S3_BUCKET_NAME}/{s3_key}")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {issue_key}: {str(e)}")
        return False

def upload_all_issues():
    """
    Upload all exported issue JSON files to S3
    """
    # Find all JSON files in the local export directory
    local_dir = "./raw/jira/CCS/"
    json_files = glob.glob(os.path.join(local_dir, "*.json"))
    
    if not json_files:
        print("No JSON files found in the export directory.")
        return
    
    print(f"Found {len(json_files)} JSON files to upload...")
    
    success_count = 0
    for json_file in json_files:
        # Extract issue key from filename (e.g., "CCS-3029.json" -> "CCS-3029")
        issue_key = os.path.splitext(os.path.basename(json_file))[0]
        
        if upload_issue_to_s3(json_file, issue_key):
            success_count += 1
    
    print(f"\n📊 Upload Summary:")
    print(f"   Total files: {len(json_files)}")
    print(f"   Successful uploads: {success_count}")
    print(f"   Failed uploads: {len(json_files) - success_count}")

if __name__ == "__main__":
    print("Starting S3 upload of exported JIRA issues...")
    upload_all_issues()
    print("S3 upload completed!")
