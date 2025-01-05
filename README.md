# AWS Policy Validator

This script audits IAM policies for specific statements using AWS Boto3 and concurrent threading.

Due to recent changes in EBS policies, AWS CloudTrail is being utilized to track the usage of these policies. Given the large number of policies, some of which are infrequently invoked, it is necessary to iterate over each policy to identify the statements that require modification.

This script is designed to handle this task efficiently, providing elasticity and concurrency to manage a high volume of policies.

The script also filters out aws managed policies.
## Requirements

- Python 3.x
- Boto3

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/JacobAmar/aws-ebs-policy-checker.git
    cd aws-ebs-policy-checker
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the script with the following command-line arguments:

- `--region`: AWS region to use (default: `us-east-1`)
- `--workers`: Number of worker threads (default: `100`)
- `--statement`: Statement to check in policies (required)

Example:
```sh
python3 main.py --region us-east-1 --workers 50 --statement ec2:CreateVolume
```

## Output

The script will generate a `found_policies.csv` file containing the ARNs of the policies that match the specified statement.

## Logging

The script logs its progress and results to the console.
