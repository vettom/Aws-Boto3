#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Perform routine ELB tasks using Boto3
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/12/2018     Initial Version                  V 1.0

"""
This script is designed to perform some common activities on AWS ELB. 
Sript uses Boto3 libraries, so it must be installed on the host running. Also expect AWS cli to be installed with at least 1 profile called default
By default Profile= Default and Region = eu-west-1 is assumed. Pass necessary argument to requirement.
"""

import boto3
import argparse
import sys

"""
Argparse allows to process. argument and set defaults. Any argument not provided will assume default value or will be None type.
list : List instances available
Start/stop : Start /stop instance and wait for action to complete and confirm result
Status : Display current status of instance.
"""
argparser = argparse.ArgumentParser(description='Perform common instance tasks')
argparser.add_argument('action', help='Instance action to be performed list/status/attach/detach')
argparser.add_argument('--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')
argparser.add_argument('--elb', default="NULL", help='Name of Aws ELB')
epilog = ("Some test extra")

args = argparser.parse_args()
try:
	# print ("INFO : Performing " + "action " + args.action " on " + args.host)
	
	print ("INFO : Performing action ", args.action, "Profile :", args.profile, "Region :", args.region )
except:
	print ("Please run -h for help, Action and Instance are minimum requirements except for list")
	sys.exit(1)

# Setting some global variables so that it can be reused.
global ec2client
global ec2resource
global Profile
global Region

Profile = args.profile
Region = args.region

def SetEC2Client(Profile, Region):
	try:
		# Sets ec2 client with profile and Region. Depending on the Boto3 funciton use client or resource.
		global ec2client
		session = boto3.Session(profile_name=Profile)
		# Set client for Classic Loadbalancer.
		ec2client = session.client('elb', region_name=Region)
	except:
		print (" ERROR : Failed to set ec2client, please ensure arguments are passed")
		sys.exit(1)

def SetEC2Resource(Profile, Region):
	try:
		# Sets ec2 client with profile and Region. Depending on the Boto3 funciton use client or resource.
		global ec2resource
		session = boto3.Session(profile_name=Profile)
		ec2resource = session.resource('ec2', region_name=Region)
	except:
		print (" ERROR : Failed to set ec2resource, please ensure arguments are passed")
		sys.exit(1)

def ListallELB():
	try: Result = ec2client.describe_load_balancers()
	except : print (" ERROR : Failed to get ELB list ")
	# Process the output and print the list
	try:
		for X in Result['LoadBalancerDescriptions']:
			print (X.get('LoadBalancerName', 'NULL'),  X.get('VPCId', 'NULL'), X.get('Instances', 'NULL'), X.get('DNSName', 'NULL'),)
	except: print("Failed to process Result to list ELB. ")
#  ------------ ****** End of modules  -------------- ******

# Starting the Main function
def main():
	SetEC2Client(Profile, Region)

	if args.action == "list":
		print("Listing available Load Balancers")
		ListallELB()
		sys.exit(0)
	elif args.action == "status":
		# Status of ELB, elb name must be provided as argument
		print ('Elb status')

	elif args.action == "attach":
		# Attache instance to elb and sho status
		print ("Attach")

	elif args.action == "detach":
		# Detach host from elb, and sho status
		print("Detach")

	else:
		print (" ERROR : Please run -h for help and provide valid option")
		sys.exit(1)






if __name__ == "__main__":
    main()
