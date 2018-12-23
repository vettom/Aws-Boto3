#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Perform routine Instance tasks using Boto3
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/12/2018     Initial Version                  V 1.0

"""
This script is designed to perform some common activities on AWS instance. 
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
argparser.add_argument('action', help='Instance action to be performed list/start/stop/restart/status')
argparser.add_argument('--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')
argparser.add_argument('--instance', default="NULL", help='Name of Aws instance')
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
def TestInstID(Var):
	if Var is 'NULL':
		print (" ERROR : Instance ID must be provided as argument. --instance i-xxxxx")
		sys.exit(1)

def SetEC2Client(Profile, Region):
	try:
		# Sets ec2 client with profile and Region. Depending on the Boto3 funciton use client or resource.
		global ec2client
		session = boto3.Session(profile_name=Profile)
		ec2client = session.client('ec2', region_name=Region)
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

def ProcessDescribeInstances(Data):
	# Process Describe instance data from AWS. Defined couple of common tags, suit your needs
	for X in Data['Reservations']:
			for Y in X["Instances"]:
				PubIP = Y.get("PublicIpAddress", "NULL")
				VPCId = Y.get("VpcId", "NULL")
				InstID = Y.get("InstanceId", "NULL")
				InstanceType = Y.get("InstanceType", "NULL")
				Status = Y.get('State').get('Name')
				# Process Tags for some default values
				for Z in Y["Tags"]:
					# Setting some default for Tad as unsure if it will exist
					if Z["Key"] == 'CMDB_hostname':
						Host = Z.get('Value', "NULL")
					try: Host
					except: Host = "Undefined"
					
					if Z["Key"] == 'Name':
						Name = Z.get('Value', "NULL")
					try: Name
					except: Name = "Undefined"

					
			try:
				print (InstID, Host, Name, PubIP, Status, VPCId,  InstanceType)
			except:
				print ("Failed to get Instance information")

def CheckInstanceStatus(Instance):
	Data = ec2client.describe_instances(InstanceIds=[Instance])
	# Process the json to print the status. Using Tag CMDB_hostname to get hostname, update if required.
	for X in Data['Reservations']:
			for Y in X["Instances"]:
				PubIP = Y.get("PublicIpAddress", "NULL")
				VPCId = Y.get("VpcId", "NULL")
				InstID = Y.get("InstanceId", "NULL")
				InstanceType = Y.get("InstanceType", "NULL")
				Status = Y.get('State').get('Name')
				# Process Tags for some default values
				for Z in Y["Tags"]:
					# Setting some default for Tad as unsure if it will exist
					if Z["Key"] == 'CMDB_hostname':
						Host = Z.get('Value', "NULL")
					try: Host
					except: Host = "Undefined"
					
			try:
				print ("Status :", Status, InstID, Host )
			except:
				print ("Failed to get status for instance ", Instance )

def StartInstance(Instance):
    try:
        # print " INFO : Starting Instance " + Instance
        ec2client.start_instances(InstanceIds=[Instance])
        waiter = ec2client.get_waiter('system_status_ok')
        waiter.wait(InstanceIds=[Instance])
        print (" INFO : Instance ", Instance, " is Ready")
    except:
        print (" ERROR : Failed to start instance ", Instance)


def StopInstance(Instance):
    try:
        # print " INFO : Stoppign instance " + Instance
        ec2client.stop_instances(InstanceIds=[Instance])
        waiter = ec2client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[Instance])
        print (" INFO : Instance ",Instance, " Stopped")
    except:
        print (" ERROR : Failed to Stop instance ", Instance)



#  ------------ ****** End of modules  -------------- ******

# Starting the Main function
def main():
	SetEC2Client(Profile, Region)
	#Take acttion based on argument specified.
	if args.action == "list":
		print (" INFO : Listing instances")
		Result = ec2client.describe_instances()
		# Pass resulting Json to Function to print result
		ProcessDescribeInstances(Result)
		
	elif args.action == "start":
		# Verify instance id provided as argument
		TestInstID(args.instance)

		print (" INFO : Starting ", args.instance)
		StartInstance(args.instance)
		sys.exit(0)
	elif args.action == "stop":
		# Verify instance id provided as argument
		TestInstID(args.instance)

		print (" INFO : Stopping ", args.instance)
		StopInstance(args.instance)
		sys.exit(0)
	elif args.action == "restart":
		# Verify instance id provided as argument
		TestInstID(args.instance)

		# Calling Stop instance function
		print (" INFO : Restarting ", args.instance)
		print ("Stopping ", args.instance)
		StopInstance(args.instance)
		# Calling start instance function
		print (" INFO : Starting ", args.instance)
		StartInstance(args.instance)
		sys.exit(0)
	elif args.action == "status":
		# Verify instance id provided as argument
		TestInstID(args.instance)

		print (" INFO : Checking status of ", args.instance)
		CheckInstanceStatus(args.instance)
		sys.exit(0)

if __name__ == "__main__":
    main()
