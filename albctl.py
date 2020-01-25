#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Perform routine ALB tasks using Boto3. Can accept mutiple ALB and Instances as arguments for attach/detach.
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3, Aws cli profiles. CMDB File, dvclass
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            25/01/2020     Initial Version                  V 1.0
# 
"""
Script for list/status/attach/detach tasks. Default variables Profile=default, Region=eu-west-1
list  : can take Topology as argument and display all ALB for the topology
Status : Accepts Topology or one or more ALB as argument and shows status
At/Detach : Accepts 1 or more ALB and Hostsor instance ID as argument. For each alb same set of actions performed with hosts
            All ALB must be in same region.
"""

import boto3,argparse,sys,time,re,os
import dvclass

SCR_HOME = os.path.dirname(os.path.realpath(__file__))


# Argument Parser with Subparse for each actopn
NOTE = "ALB Status and management"

P = argparse.ArgumentParser(description='ALB Operations tasks', epilog=NOTE)


Sub = P.add_subparsers(title="Required arguments", dest="Task")

# List  Sub Parse, requires single input which is Topology
List = Sub.add_parser("list",help="Show list of all ALB configured for Topology")
List.add_argument('-t', '--topology', help='Topology name for which ALB status to be displayed.', required=True)
List.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
# List.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

Status = Sub.add_parser("status",help="Show status of all ALB configured for Topology. Use -e or -t")
Status.add_argument('-t', '--topology', help='Topology name for which ALB status to be displayed.')
Status.add_argument('-e', '--alb', nargs='+', help='Name/s of Aws ALB')
Status.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
# Status.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

Attach = Sub.add_parser("attach",help="Attach instance/s to ALB, apply to all TG unless specified.")
Attach.add_argument('-e', '--alb', nargs='+', help='Name/s of Aws ALB', required=True)
Attach.add_argument('-t', '--target_group', default=None, help='Optional specify Target group')
Attach.add_argument('-i', '--instances', nargs='+', help='Dispatcher Hostnames or Instance ID/s', required=True)
Attach.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
# Attach.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')


Detach = Sub.add_parser("detach",help="Detach instance/s to ALB, apply to all TG unless specified.")
Detach.add_argument('-e','--alb', nargs='+', help='Name/s of Aws ALB', required=True)
Detach.add_argument('-t', '--target_group', default=None, help='Optional specify Target group')
Detach.add_argument('-i', '--instances', nargs='+', help='Dispatcher Hostnames or Instance ID/s', required=True)
Detach.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
# Detach.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

# Parse Arguments
args = P.parse_args()
# Eit programme if no arguments provided. Print help
if args.Task is None:   
        P.print_help()
        exit()

# Setting Default variables
Profile = args.profile
# Region = args.region

# Start of Functions. -----********------

def ListallALB(VPC, Region):
    # List and display all ELB in provided region. If VPC argument provided, will only show ELB attached to those VPC
    ec2client = DVboto3.SetALBClient(Profile, Region)
    try: Result = ec2client.describe_load_balancers()
    except exception as ERR: print (" ERROR : Failed to get ALB list ", ERR)
    # Process the output and print the list
    try:
        print ("\n  ALB's in {} in {} region using profile {}. " .format(VPC,Region,Profile))
        COUNT = False
        for X in Result['LoadBalancers']:
            VPCID = X.get('VpcId', 'NULL')
            if VPC == VPCID:
                ALB = X.get('LoadBalancerName', 'NULL')
                DNS = X.get('DNSName', 'NULL')
                print ("\t{} \t {} " .format(ALB, DNS))
                COUNT = True           

        if COUNT is False:
            print ("    WARNING : No ALB found, please verify Profile, Region and VPC are valid")
        # print ("\n")
    except Exception as ERR: print("Failed to process Result to list ELB. \n {}" .format(ERR))

def GetAlbList(VPC, Region):
    # Return list of ALB
    ec2client = DVboto3.SetALBClient(Profile, Region)
    try: Result = ec2client.describe_load_balancers()
    except exception as ERR: print (" ERROR : Failed to get ALB list ", ERR)
    # Process the output and print the list
    LIST = []
    try:
        # print ("\n  ALB's in {} in {} region using profile {}. " .format(VPC,Region,Profile))
        for X in Result['LoadBalancers']:
            VPCID = X.get('VpcId', 'NULL')
            if VPC == VPCID:
                # ALB = X.get('LoadBalancerName', 'NULL')
                # ARN = X.get('LoadBalancerArn', 'NULL')
                VAL = [X.get('LoadBalancerName', 'NULL'), X.get('LoadBalancerArn', 'NULL')]
                LIST.append(VAL) 
        return LIST          

    except Exception as ERR: print("Failed to process Result to list ELB. \n {}" .format(ERR))

def Albstatus(ALB, Var,Region):
    # Accepts ARN as Var
    try:
        # ALB may have multiple TG, so get tG and loop for status
        ec2client = DVboto3.SetALBClient(Profile, Region)
        Result = ec2client.describe_target_groups(
        LoadBalancerArn= Var, 
        )
        
    except Exception as ERR:
        print(" ERROR: failed to get TG Details for {}" .format(ALB))
        print(ERR)
    try:
        for X in Result['TargetGroups']:
            # TG Name and its ARN available, print Status
            TG = X.get('TargetGroupName', 'NULL')
            TGARN = X.get('TargetGroupArn', 'NULL')
            print("\n      ALB = {} Region = {} TGroup = {}\n" .format(ALB,Region,TG))
            # Now get the status of Target Group
            STATUS = ec2client.describe_target_health(TargetGroupArn=TGARN,)
            for A in STATUS['TargetHealthDescriptions']:
                B = A['Target']
                InstID = B.get('Id')
                HostName = ams.GetHostname(InstID)
                C = A['TargetHealth']
                State = C.get('State')
                print("\t  {}\t{}" .format(HostName, State))
    except Exception as ERR:
        print(" ERROR: Failed to process TG {} . \n \t{}" .format(TG, ERR))


def AttachinstancetoALB(ALBName, Instances):
    # Check all the TG and take action on all TG availalable
    # First figure out the Region from Instance information and process each Instance
    for I in Instances:
        try:
            AWSinfo = ams.GetInstAWS(I)
            InstID = AWSinfo[0]
            Host = AWSinfo[1]
            Region = AWSinfo[2]
            if InstID is None:
                print (" \nERROR : Failed to get Instance ID for {}. Please chek Instance ID/Hostname provided. " .format(I))
                exit()
        except Exception as ERR:
            print (" ERROR : Failed to get Instance ID for {} \n {} " .format(I,ERR))

        print (InstID, Host, Region, Profile)
        
def FindELBRegion(Instances):
    # Get Region Information and ensure all in single region
    try:
        REG = []
        for I in Instances:
            INFO = ams.GetInstAWS(I)
            REG.append(INFO[2])

        # If more than 1 region, exit programme
        if len(set(REG)) != 1:
            print ("  ERROR: Found more than 1 Region, all Hosts must be in same region")
            print("    Regions info found", set(REG))
            exit()
        else:
            return (REG[0])
    except Exception as ERR:
        print("    ERROR: Failed to get region info for {} \n {}" .format(I, ERR))
        exit()

def GetALBARN(ALBName, Region):
    # Find ARN for ALB provided and return
    ec2client = DVboto3.SetALBClient(Profile, Region)
    try:
        Result = ec2client.describe_load_balancers(Names=[
        ALBName,
    ],)
        X = Result['LoadBalancers']
        Y = X[0]
        ARN = Y.get('LoadBalancerArn')
        return ARN
    except Exception as ERR:
        print ("\n ERROR : Failed to get ALB ARN, check Profile and ALB name\n\n Exception :   ", ERR)
        exit()

def GetTGNameARN(ALBARN, Region):
    # With ALB ARN, find all TG attached and return result as a list TGNAme, TGARN
    try:
        ec2client = DVboto3.SetALBClient(Profile, Region)
        Result = ec2client.describe_target_groups(
            LoadBalancerArn= ALBARN, 
            )
    except Exception as ERR:
        print("  ERROR: Failed to get TG details for {} \n  Exception=" .format(ALB, ERR))

    # Loop through TargetGroup List
    LIST = []
    for X in Result['TargetGroups']:
        TG = [X.get('TargetGroupName'), X.get('TargetGroupArn')]
        LIST.append(TG)
    return LIST

def GetTGARN(ALB, ALBARN, Region, TGName):
    # I TG Neame known, get TG ARN and return it.
    try:
        ec2client = DVboto3.SetALBClient(Profile, Region)
        Result = ec2client.describe_target_groups(
            Names=[TGName,],
            )

        for X in Result['TargetGroups']:
            return X.get('TargetGroupArn')
    except Exception as ERR:
        print("  ERROR: Failed to get TG ARN for {} \n  Exception={}" .format(ALB, ERR))

def RegisterTargets(TGARN, TGNAME, ALB, Region, InstanceList):
    ec2client = DVboto3.SetALBClient(Profile, Region)
    try:
        # Register targets to provide TG ARN
        print(" INFO: Adding instance to ALB={}, TG={}" .format(ALB,TGNAME))
        Result = ec2client.register_targets( TargetGroupArn=TGARN,Targets=InstanceList,)
        if Result['ResponseMetadata']['HTTPStatusCode'] is 200:
            print (f' SUCCESS : Targets registered ')
    except Exception as ERR:
        print("\n  ERROR: Failed to register target to ALB={} TG={} \n  Exception={}" .format(ALB,TGNAME,ERR))


def DeRegisterTargets(TGARN, TGNAME, ALB, Region, InstanceList):
    ec2client = DVboto3.SetALBClient(Profile, Region)
    try:
        # Register targets to provide TG ARN
        print(" INFO: Removing instance from ALB={}, TG={}" .format(ALB,TGNAME))
        Result = ec2client.deregister_targets( TargetGroupArn=TGARN,Targets=InstanceList,)
        if Result['ResponseMetadata']['HTTPStatusCode'] is 200:
            print (f' SUCCESS : Targets Deregistered ')
    except Exception as ERR:
        print("\n  ERROR: Failed to Deregister target from ALB={} TG={} \n  Exception={}" .format(ALB,TGNAME,ERR))

# -----********------  End of Functions -----********------


# Start of Main Section. -----********------

def main():
    global Profile
    global DVboto3
    global ams
    DVboto3 = dvclass.AWSBoto3()
    ams = dvclass.AMSCMDB()


    if args.Task == "list":
        # Accepts Topology as cumpulsary argiment. 
        # Find all ALB for the Topology mentioned
        
        try:
            # First find all VPC and region, then find all ALB
            Result = ams.GetVpcReg(args.topology)
            # Make sure Result is valid, if not exit. If topology not found or not AWS, then will be empty
            if not Result:
                print ("\n ERROR : Topology not found in CMDB or it is not AWS Topology \n")
                exit()

            # At this stage we have Result with VPC and Region information
            # Result can have multiple entries for multiple regions
            for X in Result:
                Y = X.split()
                VPC = Y[0]
                REGION = Y[1]
                ListallALB(VPC, REGION)
                         
        except Exception as ERR:
            print (" ERROR : Failed to find {} in Database. Errors is {}" .format(args.topology,ERR))

    elif args.Task == "status":
        # Accepts Topology or list of ALB as argument, and at least one should be proided.
        # If elb as argument have to specify Profile and region if different.

        if args.topology is None and args.alb is None:
            print ("\n ERROR : Please provide \'-t Topology\' or \'--alb Albname's\' as argument\n")
            print (" INFO : Run \"status -h\" for help")
            exit ()
        
        # If Topology is provided process it and ignore ELB
        if args.topology:
            # Get status of all Alb from all region 
            # ec2client = boto3.SetALBClient(Profile, Region)
            Result = ams.GetVpcReg(args.topology)
            if not Result:
                print ("\n ERROR : Topology not found in CMDB or it is not AWS Topology \n")
                exit()

            for X in Result:
                Y = X.split()
                VPC = Y[0]
                REGION = Y[1]
                # Now for each VPC get list of ALB and status
                Result = GetAlbList(VPC,REGION)
                if len(Result) is not 0:
                # Now have ALB and ARN. now identify TG associated with ARN and status
                    for ALB,ARN in Result:
                        # print("\tStatus of ALB {} in {} " .format(ALB, VPC))
                        Albstatus(ALB, ARN, REGION)
                else:
                    print ("\t No ALB found in {} with Profile={}" .format(VPC, Profile, REGION))

            exit()


    elif args.Task == "attach":
        # If TG is specified, action only for that TG.
        # ALB and Instances from arguments.  
        # Get region and VPC info based on Hostname
        # Get ALB ARN, then list of TG with its ARN, then action.
        
        # Find and ensure all hosts are in same region
        Region = FindELBRegion(args.instances)
        
        # Save all instance ID to list for function.
        InstanceList = []
        for I in args.instances:
            InstID = ams.GetInstID(I)
            X = {}
            X = {'Id': InstID}
            InstanceList.append(X)
        if args.target_group is None:
            for ALB in args.alb:
                # first get ALB ARN, Target Grups and Its ARN
                ALBARN = GetALBARN(ALB, Region)
                # With ALBARN Loop through Target Group
                Result = GetTGNameARN(ALBARN, Region)
                # print(f' INFO: Processing {ALB}')
                # Result will have list of TG and TG ARN get status
                try:
                    for TGNAME,TGARN in Result:
                        # Perfor attach action on all Target Groups
                        RegisterTargets(TGARN, TGNAME, ALB, Region, InstanceList)
                except Exception as ERR:
                    print(f'\n ERROR: Failed call Register Target function \n Exception: {ERR}')

                # Sleep 10 sec before status print
                print (f' INFO: Sleeping 10sec before checking status of {ALB}')
                time.sleep(10)
                Albstatus(ALB, ALBARN, Region)
        else:
            # Process task for single TG specified
            print("Action for TG")
            for ALB in args.alb:
                # first get ALB ARN, Target Grups and Its ARN
                ALBARN = GetALBARN(ALB, Region)
                # With ALBARN Loop through Target Group
                TGARN = GetTGARN(ALB, ALBARN, Region, args.target_group)
                try:
                    RegisterTargets(TGARN, args.target_group, ALB, Region, InstanceList)
                except Exception as ERR:
                    print(f'\n ERROR: Failed call Register Target function \n Exception: {ERR}')

                # At nd sleep for few min and display status
                print (f' INFO: Sleeping 10sec before checking status of {ALB}')
                time.sleep(10)
                Albstatus(ALB, ALBARN, Region)

        exit()


    elif args.Task == "detach":

        # Find and ensure all hosts are in same region
        Region = FindELBRegion(args.instances)
        
        # Save all instance ID to list for function.
        InstanceList = []
        for I in args.instances:
            InstID = ams.GetInstID(I)
            X = {}
            X = {'Id': InstID}
            InstanceList.append(X)
        if args.target_group is None:
            for ALB in args.alb:
                # first get ALB ARN, Target Grups and Its ARN
                ALBARN = GetALBARN(ALB, Region)
                # With ALBARN Loop through Target Group
                Result = GetTGNameARN(ALBARN, Region)
                # print(f' INFO: Processing {ALB}')
                # Result will have list of TG and TG ARN get status
                try:
                    for TGNAME,TGARN in Result:
                        # Perfor attach action on all Target Groups
                        DeRegisterTargets(TGARN, TGNAME, ALB, Region, InstanceList)
                except Exception as ERR:
                    print(f'\n ERROR: Failed call Deregister Target function \n Exception: {ERR}')

                # Sleep 10 sec before status print
                print (f' INFO: Sleeping 10sec before checking status of {ALB}')
                time.sleep(10)
                Albstatus(ALB, ALBARN, Region)
        else:
            # Process task for single TG specified
            print("Action for TG")
            for ALB in args.alb:
                # first get ALB ARN, Target Grups and Its ARN
                ALBARN = GetALBARN(ALB, Region)
                # With ALBARN Loop through Target Group
                TGARN = GetTGARN(ALB, ALBARN, Region, args.target_group)
                try:
                    DeRegisterTargets(TGARN, args.target_group, ALB, Region, InstanceList)
                except Exception as ERR:
                    print(f'\n ERROR: Failed call De-register Target function \n Exception: {ERR}')

                # At nd sleep for few min and display status
                print (f' INFO: Sleeping 10sec before checking status of {ALB}')
                time.sleep(10)
                Albstatus(ALB, ALBARN, Region)

        exit()


if __name__ == "__main__":
    main()
