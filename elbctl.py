#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Perform routine ELB tasks using Boto3. Can accept mutiple ELB and Instances as arguments for attach/detach.
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli and profiles. CMDB File, dvclass
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            09/09/2019     Initial Version                  V 1.0
# DV            16/09/2019     Region info from Document        V 1.1
# 
"""
Script for list/status/attach/detach tasks. Default variables Profile=default, Region=eu-west-1
list  : can take Topology as argument and display all ELB for the topology
Status : Accepts Topology or one or more ELB as argument and shows status
At/Detach : Accepts 1 or more ELB and Hostsor instance ID as argument. For each elb same set of actions performed with hosts
            All ELB must be in same region.
"""

import boto3,argparse,sys,time,re,os
import dvclass

SCR_HOME = os.path.dirname(os.path.realpath(__file__))


# Argument Parser with Subparse for each actopn
NOTE = "ELB Status"

P = argparse.ArgumentParser(description='ELB Operations tasks', epilog=NOTE)


Sub = P.add_subparsers(title="Required arguments", dest="Task")

# List  Sub Parse, requires single input which is Topology
List = Sub.add_parser("list",help="Show list of all ELB configured for Topology")
List.add_argument('-t', '--topology', help='Topology name for which ELB status to be displayed.', required=True)
List.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
List.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

Status = Sub.add_parser("status",help="Show status of all ELB configured for Topology")
Status.add_argument('-t', '--topology', help='Topology name for which ELB status to be displayed.')
Status.add_argument('-e', '--elb', nargs='+', help='Name/s of Aws ELB')
Status.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
Status.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

Attach = Sub.add_parser("attach",help="Attach instance/s to ELB")
Attach.add_argument('-e', '--elb', nargs='+', help='Name/s of Aws ELB', required=True)
Attach.add_argument('-i', '--instances', nargs='+', help='Dispatcher Hostnames or Instance ID/s', required=True)
Attach.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
Attach.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')


Detach = Sub.add_parser("detach",help="Detach instance/s to ELB")
Detach.add_argument('-e','--elb', nargs='+', help='Name/s of Aws ELB', required=True)
Detach.add_argument('-i', '--instances', nargs='+', help='Dispatcher Hostnames or Instance ID/s', required=True)
Detach.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
Detach.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

# Parse Arguments
args = P.parse_args()
# Eit programme if no arguments provided. Print help
if args.Task is None:   
        P.print_help()
        exit()

# Setting Default variables
Profile = args.profile
Region = args.region

# Start of Functions. -----********------

def ListallELB(VPC, Region):
    # List and display all ELB in provided region. If VPC argument provided, will only show ELB attached to those VPC
    ec2client = boto3.SetELBClient(Profile, Region)
    try: Result = ec2client.describe_load_balancers()
    except exception as ERR: print (" ERROR : Failed to get ELB list ", ERR)
    # Process the output and print the list
    try:
        print ("\n  ELB's in {} in {} region using profile {}. " .format(VPC,Region,Profile))
        for X in Result['LoadBalancerDescriptions']:
            ELB = X.get('LoadBalancerName', 'NULL')
            VPCID = X.get('VPCId', 'NULL')
            if VPC == VPCID:
                print ("  {} " .format(ELB))
                

        print ("\n")
    except: print("Failed to process Result to list ELB. ")

def Elbstatus(Var,Region):
    # Var = ELB name
    ec2client = boto3.SetELBClient(Profile, Region)
    try:
        print("\n  ELB {} in {}  " .format(Var, Region))
        Result = ec2client.describe_instance_health(LoadBalancerName=Var)
        # Process Result and display
        for X in Result['InstanceStates']:
            InstID = X.get('InstanceId')
            InstName = ams.GetHostname(InstID)
            print (InstName, '\t', InstID, '\t', X.get('State'))

    except Exception as ERR:
        print(" ERROR : Failed to get ELB status using ELB={}, Region={}, Profile={}. \n ERROR : {}" .format(Var,Region,Profile,ERR))
    # 
    # Now process Result and Get hostname to print.
def GetElbList(VPC, Region):
    # Return list of ELB 
    ec2client = boto3.SetELBClient(Profile, Region)
    try: Result = ec2client.describe_load_balancers()
    except exception as ERR: print (" ERROR : Failed to get ELB list ", ERR)
    # Process the output and print the list
    LIST = []
    try:
        for X in Result['LoadBalancerDescriptions']:
            ELB = X.get('LoadBalancerName', 'NULL')
            VPCID = X.get('VPCId', 'NULL')
            if VPC == VPCID:
                LIST.append(ELB)
        return LIST
    except: print("Failed to process Result to list ELB. ")   

def AtachinstancetoELB(ELB, Instances):
    # Loop through Instances and issue attach command
    for I in Instances:
        try: 
            # Call function that gets instance information like ID,host, Region, AZ, VPC
            global Region
            AWSinfo = ams.GetInstAWS(I)
            InstID = AWSinfo[0]
            Host = AWSinfo[1]
            Region = AWSinfo[2]
            if InstID is None:
                print (" \nERROR : Failed to get Instance ID for {}. Please chek Instance ID/Hostname provided. " .format(I))
                exit()
        except Exception as ERR:
            print (" ERROR : Failed to get Instance ID for {} \n {} " .format(I,ERR))

        try:
            ec2client = boto3.SetELBClient(Profile, Region)
            Result = ec2client.register_instances_with_load_balancer(\
                LoadBalancerName=ELB, \
                Instances=[{'InstanceId': InstID},])
            
            print (" INFO : Attached {} to ELB {}.  " .format(Host,ELB))
        except Exception as ERR:
            print (" \nERROR: Failed to attach Host {} {} to {} \n {}" .format(Host,InstID,ELB,ERR))


def DetachfromELB(ELB, Instances):
    # Loop through Instances and issue attach command
    for I in Instances:
        try: 
            # Call function that gets instance information like ID,host, Region, AZ, VPC
            global Region
            AWSinfo = ams.GetInstAWS(I)
            InstID = AWSinfo[0]
            Host = AWSinfo[1]
            Region = AWSinfo[2]
            if InstID is None:
                print (" \nERROR : Failed to get Instance ID for {}. Please chek Instance ID/Hostname provided. " .format(I))
                exit()
        except Exception as ERR:
            print (" ERROR : Failed to get Instance ID for {} \n {} " .format(I,ERR))

        try:
            ec2client = boto3.SetELBClient(Profile, Region)
            Result = ec2client.deregister_instances_from_load_balancer(\
                LoadBalancerName=ELB, \
                Instances=[{'InstanceId': InstID},])
            
            print (" INFO : Detached {} from ELB {}. " .format(Host,ELB))
        except Exception as ERR:
            print (" \nERROR: Failed to detach Host {} {} to {} \n {}" .format(Host,InstID,ELB,ERR))

# Start of Main Section. -----********------

def main():
    global boto3
    global ams
    boto3 = dvclass.AWSBoto3()
    ams = dvclass.AMSCMDB()
    # Set ec2 client from Class
    ec2client = boto3.SetELBClient(Profile, Region)
    


    if args.Task == "list":
        # Accepts Topology as cumpulsary argiment. 
        # Find all ELB for the Topology mentioned
        #  . First find all VPC and region, then find all ELB
        try:
            Result = ams.GetVpcReg(args.topology)
            # Make sure Result is valid, if not exit. If topology not found or not AWS, then will be empty
            if not Result:
                print ("\n ERROR : Topology not found in CMDB or it is not AWS Topology \n")
                exit()

            # At this stage we have Result with values, so continue
            # Result can have multiple entries for multiple regions
            for X in Result:
                Y = X.split()
                VPC = Y[0]
                REGION = Y[1]
                ListallELB(VPC, REGION)
                
                
        except Exception as ERR:
            print (" ERROR : Failed to find {} in Database. Errors is {}" .format(args.topology,ERR))
        
        

    elif args.Task == "status":
        # Accepts Topology or list of ELB as argument, and at least one should be proided.
        # If elb as argument have to specify Profile and region if different.

        if args.topology is None and args.elb is None:
            print ("\n ERROR : Please provide \'-t Topology\' or \'--elb Elbname\' as argument\n")
            print (" INFO : Run \"status -h\" for help")
            exit ()
        
        # If Topology is provided process it and ignore ELB
        if args.topology:
            # Get status of all elb from all region
            ec2client = boto3.SetELBClient(Profile, Region)
            Result = ams.GetVpcReg(args.topology)
            if not Result:
                print ("\n ERROR : Topology not found in CMDB or it is not AWS Topology \n")
                exit()

            for X in Result:
                Y = X.split()
                VPC = Y[0]
                REGION = Y[1]
                # Now for each VPC get list of ELB and status
                Result = GetElbList(VPC,REGION)
                for ELB in Result:
                    Elbstatus(ELB, REGION)
            exit()

        if args.elb:
            for ELB in args.elb:
                # Call the elbstatus function
                Elbstatus(ELB,Region)
            exit()


    elif args.Task == "attach":
        #Loop through the ELB provided and call attach function. At end wait few seconds before issuing status
        for ELB in args.elb:
            AtachinstancetoELB(ELB, args.instances)

        # At end sleep for few seconds then status
        print ("\n INFO : Waiting 20 seconds before checking status...")
        time.sleep(20)
        for ELB in args.elb:
            Elbstatus(ELB,Region)



    elif args.Task == "detach":
        #Loop through the ELB provided and call attach function. At end wait few seconds before issuing status
        for ELB in args.elb:
            DetachfromELB(ELB, args.instances)

        # At end sleep for few seconds then status
        print ("\n INFO : Waiting 20 seconds before checking status...")
        time.sleep(20)
        for ELB in args.elb:
            Elbstatus(ELB,Region)
        

    







if __name__ == "__main__":
    main()