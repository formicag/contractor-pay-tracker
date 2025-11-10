#!/usr/bin/env python3
"""
Bulk upload all files from InputData/ to S3
"""
import boto3
import glob
import os
from concurrent.futures import ThreadPoolExecutor

AWS_PROFILE = "AdministratorAccess-016164185850"
AWS_REGION = "eu-west-2"
BUCKET_NAME = "contractor-pay-files-development-016164185850"
S3_PREFIX = "production"
INPUT_DIR = "/Users/gianlucaformica/Projects/contractor-pay-tracker/InputData"

session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
s3 = session.client('s3')

def upload_file(file_path):
    """Upload a single file to S3"""
    filename = os.path.basename(file_path)
    key = f"{S3_PREFIX}/{filename}"

    try:
        s3.upload_file(file_path, BUCKET_NAME, key)
        return f"✅ {filename}"
    except Exception as e:
        return f"❌ {filename}: {str(e)}"

# Get all Excel files
files = glob.glob(f"{INPUT_DIR}/*.xlsx")
print(f"📤 Uploading {len(files)} files...")

# Upload in parallel (10 at a time)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_file, files))

for result in results:
    print(result)

print(f"\n✅ Upload complete! {len(files)} files uploaded.")
