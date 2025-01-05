import boto3
import logging
import time
import csv
import argparse
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_iam_policies(region):
    # Create an IAM client in the specified region
    iam_client = boto3.client('iam', region_name=region)
    
    # Create a paginator to handle large number of policies
    paginator = iam_client.get_paginator('list_policies')
    
    # List to store all policy ARNs
    policy_arns = []
    
    # Iterate through the pages of policies and collect their ARNs
    for page in paginator.paginate(Scope='All'):
        for policy in page['Policies']:
            # Filter out managed AWS policies https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#aws-managed-policies
            if not policy['Arn'].startswith('arn:aws:iam::aws:policy/'):
                policy_arns.append(policy['Arn'])
    
    return policy_arns

def print_policy_document(policy_arn, region, statement_to_check):
    logging.info(f"Started to check policy arn: {policy_arn}")
    iam_client = boto3.client('iam', region_name=region)
    policy_version = iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
    policy_document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
    
    statements = policy_document['Statement']
    found = False
    for statement in statements:
        if 'Action' in statement and statement_to_check in statement['Action']:
            found_policies.append(policy_arn)
            found = True
            break

def check_policies_in_threads(policy_arns, region, statement_to_check, num_workers):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(lambda policy_arn: print_policy_document(policy_arn, region, statement_to_check), policy_arns)

def write_to_csv(found_policies):
    with open('found_policies.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Policy ARN'])
        for policy_arn in found_policies:
            writer.writerow([policy_arn])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check IAM policies for specific statements.')
    parser.add_argument('--region', type=str, default='us-east-1', help='AWS region to use')
    parser.add_argument('--workers', type=int, default=100, help='Number of worker threads')
    parser.add_argument('--statement', type=str, required=True, help='Statement to check in policies')
    args = parser.parse_args()

    start_time = time.time()
    found_policies = []
    policy_arns = list_iam_policies(args.region)
    check_policies_in_threads(policy_arns, args.region, args.statement, args.workers)
    logging.info(f"Found {len(found_policies)} policies with {args.statement}")
    logging.info(f"List of found policies: {found_policies}")
    logging.info(f"Total number of IAM policies checked: {len(policy_arns)}")
    write_to_csv(found_policies)
    end_time = time.time()
    logging.info(f"Time taken: {end_time - start_time} seconds")