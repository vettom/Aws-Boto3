#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Start/stop instances. Status of instance or all instances in topology.
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli profiles. CMDB File, dvclass
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            25/02/2020     Initial Version                  V 1.0
# DV            29/02/2020     rewrited for dvclass             V 2.0
# 
'''
Take hostname or instance ID as argument and perform action 
Accepts Topoogy as argument and show status of all hosts in topology.

'''

import boto3,argparse,sys,time,re,os
import dvclass

argparser = argparse.ArgumentParser(description='Perform common instance tasks')
argparser.add_argument('Task', choices=['start','stop','restart','status', 'topo'], help='Instance action to be performed list/start/stop/restart/status')
argparser.add_argument('-i', '--instance', nargs='+', help='Hostnames or Aws instance IDs' )
argparser.add_argument('-t', '--topology', help='Topology name to get status of all instances' )
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
# argparser.add_argument('--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

args = argparser.parse_args()

def InstanceStatus(Instance, Host, Region):
    # Set ec2 client 
    ec2client =DVboto3.SetEC2Client(Profile, Region)
    try:
        # Get instance details
        Data = ec2client.describe_instances(InstanceIds=[Instance])
        # Process the json to print the status. Using Tag CMDB_hostname to get hostname, update if required.
    except Exception as ERR:
        print(f'  ERROR: Failed to gent instance details, please ensure right profile and is AWS topology \n   Exception is {ERR}')
        exit()

    for X in Data['Reservations']:
            for Y in X["Instances"]:
                InstID = Y.get("InstanceId", "NULL")
                InstanceType = Y.get("InstanceType", "NULL")
                Status = Y.get('State').get('Name')
                    
            try:
                print (f'  {Host} \t {Status}' )
            except:
                print ("  ERROR: Failed to get status for Host ", Host )


def StopInstance(Instance, Host, Region):
    # Set ec2 client 
    ec2client =DVboto3.SetEC2Client(Profile, Region)
    try:
        # print " INFO : Stoppign instance " + Instance
        print(f'  INFO: Executing stop on {Host}.')
        ec2client.stop_instances(InstanceIds=[Instance])
        print(f'  INFO: Waiting for {Host} to stop.')
        waiter = ec2client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[Instance])
        print (f'  INFO: {Host} stopped.')
    except:
        print (" ERROR : Failed to Stop instance ", Host)


def StartInstance(Instance, Host, Region):
    # Set ec2 client 
    ec2client =DVboto3.SetEC2Client(Profile, Region)
    try:
        # print " INFO : Stoppign instance " + Instance
        print(f'  INFO: Executing start on {Host}.')
        ec2client.start_instances(InstanceIds=[Instance])
        print(f'  INFO: Waiting for {Host} to start.')
        waiter = ec2client.get_waiter('system_status_ok')
        waiter.wait(InstanceIds=[Instance])
        print (f'  INFO: {Host} started.')
    except:
        print (" ERROR : Failed to Start instance ", Host)


def VerifyInstArgument(Arg):
    if Arg is None:
        print("  ERROR: Instance name must be provided as argument. -h for help ")
        argparser.print_help()
        exit()

def main():
    global Profile
    global DVboto3
    global ams
    Profile = args.profile
    DVboto3 = dvclass.AWSBoto3()
    ams = dvclass.AMSCMDB()
    
    # Ready to take action based on input
    if args.Task == "status":
        VerifyInstArgument(args.instance)
        print("\n")
        # Loop through instance and take action
        for X in args.instance:
            Result = ams.GetInstAWS(X)
            # instance_id, Host, Region, AZ, VPC
            InstID = Result[0]
            HostName = Result[1]
            Region = Result[2]
            InstanceStatus(InstID,HostName,Region)
        print("\n")

    elif args.Task == "stop":
        VerifyInstArgument(args.instance)
        print("\n")
        # Loop through instance and take action
        for X in args.instance:
            Result = ams.GetInstAWS(X)
            # instance_id, Host, Region, AZ, VPC
            InstID = Result[0]
            HostName = Result[1]
            Region = Result[2]
            StopInstance(InstID,HostName,Region)

        print("\n")

    elif args.Task == "start":
        VerifyInstArgument(args.instance)
        print("\n")
        # Loop through instance and take action
        for X in args.instance:
            Result = ams.GetInstAWS(X)
            # instance_id, Host, Region, AZ, VPC
            InstID = Result[0]
            HostName = Result[1]
            Region = Result[2]
            StartInstance(InstID,HostName,Region)

        print("\n")

    elif args.Task == "restart":
        VerifyInstArgument(args.instance)
        print("\n")

        for X in args.instance:
            Result = ams.GetInstAWS(X)
            # instance_id, Host, Region, AZ, VPC
            InstID = Result[0]
            HostName = Result[1]
            Region = Result[2]
            StopInstance(InstID,HostName,Region) 
            time.sleep(3)
            StartInstance(InstID,HostName,Region)    

    elif args.Task == "topo":
        # Print status of all instances in topology
        # Topology as argument required
        if args.topology is None:
            print( "  ERROR: Topology argument must be provided. -h for help")
            exit()

        # Get instance information for topology and get status.
        Result = ams.GetInstanceforTopo(args.topology)
        if len(Result) is 0:
            print(f'  ERROR: No instances found for {args.topology}, verify topology name and is it AWS topology? \n')
            exit()
        
        print("\n")
        # Loop through instance and take action
        for X in Result:
            Result = ams.GetInstAWS(X)
            # instance_id, Host, Region, AZ, VPC
            InstID = Result[0]
            HostName = Result[1]
            Region = Result[2]
            InstanceStatus(InstID,HostName,Region)
        print("\n")


if __name__ == "__main__":
    main()