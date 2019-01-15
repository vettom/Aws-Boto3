# Python - Aws Boto3 Scripts

Scripts to manage AWS instances with help of Python-Boto3 libraries. All scripts will be written on Python 3.7 and later. Expects AWS CLI to be configured and and profile defined.

- ec2instance : Perform common Instance tasks list/start/stop/restart/status
$ec2instance.py [-h] [--profile PROFILE] [--region REGION]
                      [--instance INSTANCE]
                      action
- elbctl 	: Control ELB, not ready.
$elbctl.py [-h] -a ACTION [-p PROFILE] [-r REGION] [--elb ELB [ELB ...]]
                 [--vpc VPC [VPC ...]] [-i INSTANCES [INSTANCES ...]]
