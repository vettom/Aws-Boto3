#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Perform routine ELB tasks using Boto3. Can accept mutiple ELB and Instances as arguments for attach/detach.
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli and profiles
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/12/2018     Initial Version                  V 1.0


"""
Script for list/status/attach/detach tasks. Default variables Profile=default, Region=eu-west-1
list : lists all available ELB in provided region
list vpc : If VPC (can be multiple) provided as argument elb attached to VPC only displayed
status : Accepts one or more ELB as argument and display status
attach/detach : This action can take multiple elb and instances argument. Instances will treated same for all elb mentioned.
eg elbctl.py -a attach --profile profile1 --region eu-central-1 --vpc vpc-1 vpc-1 --instances i-instance1 i-instance2
Above command attach 2 instanced to 2 separate elb in same region.
"""

import boto3
import argparse
import sys
import time


argparser = argparse.ArgumentParser(description='ELB Operations tasks')
argparser.add_argument('-a', '--action', help='list/status/attach/detach', required=True)
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')
argparser.add_argument('--elb', nargs='+', help='Name/s of Aws ELB')
argparser.add_argument('--vpc', nargs='+', help='Name/s of Aws VPC')
argparser.add_argument('-i', '--instances', nargs='+', help='Instance ID/s')

args = argparser.parse_args()
try:
	# print ("INFO : Performing " + "action " + args.action " on " + args.host)
	
	print ("\nINFO : Performing action ", args.action, "Profile =", args.profile, "Region =", args.region, "\n")
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


def Elbstatus(Var):
	# Status of the ELB, accept ELB name as argument.
	try:
		Result = ec2client.describe_instance_health(LoadBalancerName=Var)
	except:
		print(" ERROR: Failed to get status for ELB ", Var)

	print ("\nStatus of ELB ", Var)
	for X in Result['InstanceStates']:
		print (X.get('InstanceId'), '\t', X.get('State'))
	


def ListallELB():
	# List and display all ELB in provided region. If VPC argument provided, will only show ELB attached to those VPC
	try: Result = ec2client.describe_load_balancers()
	except : print (" ERROR : Failed to get ELB list ")
	# Process the output and print the list
	try:
		for X in Result['LoadBalancerDescriptions']:
			ELB = X.get('LoadBalancerName', 'NULL')
			VPCId = X.get('VPCId', 'NULL')
			InstID = []
			for Y in X['Instances']:
				InstID.append(Y.get('InstanceId'))
			# If VPC is specified print ELB in that VPC only
			if args.vpc is None:
				print (ELB,"\t", VPCId,"\t", InstID)
			else:
				for Y in args.vpc:
					if Y == VPCId:
						print (ELB,"\t", VPCId,"\t", InstID)

	except: print("Failed to process Result to list ELB. ")


def DetachfromELB(ELB, Instances):
	# Loop through instances and issue detach command
	for I in Instances:
		try:
			Result = ec2client.deregister_instances_from_load_balancer(\
				LoadBalancerName=ELB, \
				Instances=[{'InstanceId': I},])
			print ( "INFO :", I, " removed from ELB ", I, ELB)
		except:
			print (" ERROR: Failed to detach instance ", I)


def AtachinstancetoELB(ELB, Instances):
	# Loop through Instances and issue attach command
	for I in Instances:
		try:
			Result = ec2client.register_instances_with_load_balancer(\
				LoadBalancerName=ELB, \
				Instances=[{'InstanceId': I},])
			print (" INFO :", I, " attached to ELB ", ELB)
		except:
			print (" ERROR: Failed to attach instance ", I)

#  ------------ ****** End of modules  -------------- ******

# Starting the Main function
def main():
	SetEC2Client(Profile, Region)

	if args.action == "list":
		# print("Listing available Load Balancers in ", Region, "with profile ", Profile)
		ListallELB()
		sys.exit(0)
	elif args.action == "status":
		# ec2client.describe_instance_health(LoadBalancerName='barclaysprod63')
		if args.elb is None:
			print ("--elb is required field, please run -h for help")
			argparser.print_help()
			exit()
		else:
			for ELB in args.elb:
				# Call the elbstatus function
				Elbstatus(ELB)

	elif args.action == "attach":
		# Attache instance to elb and show status of elb
		if args.elb is None or args.instances is None:
			argparser.print_help()
			print(" Error: ELB and Instances are required argument for Attach/detach ")
			exit()
		for ELB in args.elb:
			AtachinstancetoELB(ELB, args.instances)

		print("\n INFO : Sleeping 5 sec before checking status")	
		time.sleep(5)
		for ELB in args.elb:
			Elbstatus(ELB)

	elif args.action == "detach":
		# Detach host/s from elb/s, and sho status
		print (args.elb, "Instance:", args.instances)
		if args.elb is None or args.instances is None:
			argparser.print_help()
			print(" Error: ELB and Instances are required argument for Attach/detach ")
			exit()

		# Now that input is verified, call function and pass vales
		# First Loop throuh ELB and call function for each VPC
		for ELB in args.elb:
			DetachfromELB(ELB, args.instances)
		print(" \nINFO : Sleeping 5 sec before checking status")
		time.sleep(5)
		for ELB in args.elb:
			Elbstatus(ELB)


	else:
		print (" ERROR : Please run -h for help and provide valid option")
		sys.exit(1)






if __name__ == "__main__":
    main()
