#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : List all security group rules attached to EC2.
#         : Check if specified IP's are whitelisted on resource     or not
# Author:       Denny Vettom
# Web : https://vettom.github.io/ 
# Dependencies: PYTHON -3, Boto3, Aws cli profiles, argparse, netaddr
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/05/2020     Initial Version                  V 1.0
# 
"""
Generic script does not rely on dvclass or CMDB. Requires all the Pyton modules mentioned above.
- Accept EC2 Instance ID, Profile and region to print all SG rules
- Accept EC2 Instance ID, source IP addresses Region and Profile to validate if IP is whitelisted or not.
- Help for command available with -h argument
"""

try:
    import boto3,argparse,os,time 
    from netaddr import IPNetwork, IPAddress
except Exception as ERR:
    print(f' ERROR: Failed to import module. {ERR}' )
    exit()

SCR_HOME = os.path.dirname(os.path.realpath(__file__))


# ----- Input section ----
# Argument Parser with Subparse for each actopn
NOTE = "Ec2 Instance Security Group list/print ingress, check if IP whitelisted. \n Profile and Regin defaults to 'default' and 'eu-west-1' unless provided as argument. Requires Credentials to be stored in AWS cli configuration format."

P = argparse.ArgumentParser(description='Print all SG rules or check if specified IP addresses are whitelisted for Instance or not.', epilog=NOTE)
Sub = P.add_subparsers(title="Required arguments", dest="Task")


# ALB Sub Parse
EC2 = Sub.add_parser("ec2",help="Print all SecurityGroup Rules attached to ALB")
EC2.add_argument('-i', '--instanceid', help='Instance ID of host', required=True)
EC2.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
EC2.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')



 
EC2i = Sub.add_parser("ec2check",help="Check if provided IP/s are whitelisted on ALB and prints rule and ServiceGroup name")
EC2i.add_argument('-i', '--instanceid', help='Instance ID of host', required=True)
EC2i.add_argument('-s', '--sourceip', nargs='+', help='IP Addresses to check space separated.', required=True)
EC2i.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
EC2i.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')




# Parse Arguments
args = P.parse_args()

# Eit programme if no arguments provided. Print help
if args.Task is None:   
        P.print_help()
        exit()

#  --- Endof nputs ---

#  ------ Start of functions ------ 

def Err(Var): print("\033[1;41m\033[93m  {} \033[00m \n" .format(Var))  # Yellow on Red
def Warn(Var): print("\033[1;44m\033[93m  {} \033[00m \n" .format(Var)) # Yellow on Black
def Info(Var): print("\033[1;44m\033[32m  {} \033[00m \n" .format(Var)) # Green on Black
def R(Var): print("\033[1;31m {}\033[00m" .format(Var))
def Y(Var): print("\033[1;93m {}\033[00m" .format(Var))
def G(Var): print("\033[1;32m {}\033[00m" .format(Var))
def B(Var): print("\033[1;35m {}\033[00m" .format(Var))
def R1(Var): print("\033[1;41m\033[97m {} \033[00m" .format(Var))
def G1(Var): print("\033[1;42m\033[97m {} \033[00m" .format(Var))
def B1(Var): print("\033[1;44m\033[97m {} \033[00m" .format(Var))


def SetEC2Client( Profile, Region):
        global ec2client
        # Sets ec2 client with profile and Region.
        try:
            session = boto3.Session(profile_name=Profile)
            ec2client = session.client('ec2', region_name=Region)
            return ec2client
        except Exception as ERR:
            Err(f' ERROR: Action failed. Error is {ERR}')
            exit()

def BuildEC2Whitelist():
    global ec2client
    try:
        ec2client = SetEC2Client(Profile, Region)
        Result = ec2client.describe_instances(InstanceIds=[InstID])

    except Exception as ERR:
        Err(ERR)
        Err(f"Failed to configure EC2 Client and run describe on instance. Check instance name, region and profile")
        exit()
    try:
            # Process result
            for X in Result['Reservations']:
                for Y in X['Instances']:
                    for Z in Y['SecurityGroups']:
                        SGroup = Z['GroupId']
                        ReturnIngress(SGroup,Profile,Region)
                        

                        

    except Exception as ERR:
        cprint.Err(f"{ERR}")
        exit()

def ReturnIngress(sgroup,profile,region):
    # List all Ingress rules and update Global variable for processing.
    try:
        # Set EC2 client to print SG rules
        ec2client = SetEC2Client(Profile, Region)
    except Exception as ERR:
        Err(f"{ERR}")
    
    try:
        # Get ingress rules
        Result = ec2client.describe_security_groups( GroupIds=[sgroup]         )
    except Exception as ERR:
        Err(f" {ERR} \n  ERROR: Failed to describe Security Group")

    try:
        global WhiteList
        Var = []

        for X in Result['SecurityGroups']:
            for Y in X['IpPermissions']:
                # Loop through IPV4 whitlists
                for A in Y['IpRanges']:
                    
                    Var = [A.get('CidrIp'), sgroup, Y['FromPort'], Y['ToPort'] ]
                    if Var is not None:
                        WhiteList.append(Var)
    except Exception as ERR:
        Err(f" {ERR} \n  ERROR: Failure to process Security Group Ingress")



def ValidateIPV4(VAR):
    try:
        i = IPAddress(VAR)
    except:
        Err(f" ERROR: {VAR} not valid IP v4 Address.")
        exit()

def TestIPWhitelist(IPA):
    try:
        Stat = False
        for Rule,SGname,From,To in WhiteList:
            # Check if IP is Whitelisted
            if IPAddress(IPA) in IPNetwork(Rule):
                G(f"      {IPA} allowed in SG={SGname} Rule={Rule} Ports {From}-{To}")
                Stat = True
        # If not whitelisted print that
        if Stat is False:
            # Means no matching rule found
            Warn(f"     {IPA} not whitelisted.")
            print("")
    except Exception as ERR:
        Err(ERR)

#  ------ End of functions ------ 


def main():
    global Region,Profile,WhiteList,InstID
    Profile = args.profile
    Region = args.region
    WhiteList = []
    InstID = args.instanceid

    if args.Task == "ec2":
        Y(f" INFO : Printing SG rules attached to Instance {args.instanceid} using Profile={Profile}, Region={Region}")
        # Create whitelist with all SG Rules.
        BuildEC2Whitelist()

        try:
            # Pront rules 
            for Rule,SGname,From,To in WhiteList:
                G(f"{SGname}  {Rule}  {From} - {To} ")
                
            print()
        except Exception as ERR:
            Err(ERR)



    elif args.Task == "ec2check":
        # CHeck specified IP whitelisted or not
        Y(f" INFO: Checking IP whitelisting on {InstID} using Profile={Profile}, Region={Region}. ")

        # Verify that provided IP are valid IPv4
        for IP in args.sourceip:
            ValidateIPV4(IP)

        # Call script to build list of Whitelists
        BuildEC2Whitelist()

        # Now ready to validate each IP
        for IP in args.sourceip:
            TestIPWhitelist(IP)





if __name__ == "__main__":
    main()