#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : List all security group rules attached to ALB/ELB.
#         : Check if specified IP's are whitelisted or not
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
- Accept LB name, Profile and region to print all SG rules
- Accept LB Name, source IP addresses Region and Profile to validate if IP is whitelisted or not.
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
NOTE = "ELB/ALB Security Group list/print ingress, check if IP whitelisted. \n Profile and Regin defaults to 'default' and 'eu-west-1' unless provided as argument. Requires Credentials to be stored in AWS cli configuration format. \n Instance check will gt Bpbu and region from CMDB "

P = argparse.ArgumentParser(description='Print all SG rules or check if specified IP addresses are whitelisted for LB or not.', epilog=NOTE)
Sub = P.add_subparsers(title="Required arguments", dest="Task")


# ALB Sub Parse
ALB = Sub.add_parser("alb",help="Print all SecurityGroup Rules attached to ALB")
ALB.add_argument('-l', '--lbname', help='Name of ALB', required=True)
ALB.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
ALB.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

ELB = Sub.add_parser("elb",help="Print SecurityGroup all Rules attached to ALB")
ELB.add_argument('-l', '--lbname', help='Name of ALB', required=True)
ELB.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
ELB.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

 
ALBi = Sub.add_parser("albcheck",help="Check if provided IP/s are whitelisted on ALB and prints rule and ServiceGroup name")
ALBi.add_argument('-l', '--lbname', help='Name of ALB', required=True)
ALBi.add_argument('-s', '--sourceip', nargs='+', help='IP Addresses to check space separated.', required=True)
ALBi.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
ALBi.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')

ELBi = Sub.add_parser("elbcheck",help="Check if IP/s are whitelisted on ELB and prints rule and ServiceGroup name")
ELBi.add_argument('-l', '--lbname',  help='Name of ELB', required=True)
ELBi.add_argument('-s', '--sourceip', nargs='+', help='IP Addresses to check space separated.', required=True)
ELBi.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
ELBi.add_argument('-r', '--region', default="eu-west-1", help='Default is eu-west-1, or provide as argument')



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

def SetALBClient(Prof, Reg):
    # print(Prof, Reg)
    try:
        # Sets elb client with profile and Region. Depending on the Boto3 funciton use client or resource.
        session = boto3.Session(profile_name=Prof)
        # Set client for Classic Loadbalancer.
        ec2client = session.client('elbv2', region_name=Reg)
        return ec2client
    except Exception as ERR:
        Err(f" ERROR : Failed to set ec2client, please ensure arguments are passed. \n {ERR}" )
        exit(1)

def SetELBClient(Prof, Reg):
        try:
            # Sets elb client with profile and Region. Depending on the Boto3 funciton use client or resource.
            session = boto3.Session(profile_name=Prof)
            # Set client for Classic Loadbalancer.
            ec2client = session.client('elb', region_name=Reg)
            return ec2client
        except Exception as ERR:
            COLOR.Err(f" ERROR : Failed to set ec2client, please ensure arguments are passed." )
            COLOR.Err(ERR)
            exit(1)

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

def BuildALBWhitelist():
    try:
        SetALBClient(Profile,Region)
        ec2client = SetALBClient(Profile, Region)
        Result = ec2client.describe_load_balancers(Names=[args.lbname],)
    except Exception as ERR: 
        Err(f" ERROR : Failed to execute describe on {args.lbname}  ")
        Err(ERR)
        exit()

    # Get list of Security Groups attached.
    try:
        for X in Result['LoadBalancers']:
            SG = X.get('SecurityGroups', None)

            # Loop through SG if not none
            if SG is not None:
                # Loop Through group to get list of rules in Whitelist
                Info(f"Procssing SG {SG}")
                print("")
                time.sleep(3)

                for SGroup in SG:
                    ReturnIngress(SGroup,Profile,Region)
            else:
                Err(f" ERROR: Failed to get Service Group list.")
                exit()
    except Exception as ERR:
        Err(ERR)
        exit()

def BuildELBWhitelist():
    try:
        SetALBClient(Profile,Region)
        ec2client = SetELBClient(Profile, Region)
        Result = ec2client.describe_load_balancers(LoadBalancerNames=[args.lbname],)
    except Exception as ERR: 
        Err(f" ERROR : Failed to execute describe on {args.lbname}  ")
        Err(ERR)
        exit()
    # Get list of Security Groups attached.
    try:
        for X in Result['LoadBalancerDescriptions']:
            SG = X.get('SecurityGroups', None)

            # Loop through SG if not none
            if SG is not None:
                # Loop Through group to get list of rules in Whitelist
                Info(f" Procssing SG {SG}")
                print("")
                time.sleep(3)

                for SGroup in SG:
                    ReturnIngress(SGroup,Profile,Region)
            else:
                Err(f" ERROR: Failed to get Service Group list.")
                exit()
    except Exception as ERR:
        Err(ERR)
        exit()


def ReturnIngress(sgroup,profile,region):
    # List all Ingress rules and update Global variable for processing.
    try:
        # Set EC2 client to print SG rules
        ec2client = SetEC2Client(Profile, Region)
    except Exception as ERR:
        cprint.Err(f"{ERR}")
    
    try:
        # Get ingress rules
        Result = ec2client.describe_security_groups( GroupIds=[sgroup]         )
    except Exception as ERR:
        cprint.Err(f" {ERR} \n  ERROR: Failed to describe Security Group")

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
        cprint.Err(f" {ERR} \n  ERROR: Failure to process Security Group Ingress")

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
    global Region,Profile,WhiteList
    Profile = args.profile
    Region = args.region
    WhiteList = []

    if args.Task == "alb":
        Y(f" INFO : Printing SG rules attached to ALB {args.lbname} using Profile={Profile}, Region={Region}")
        BuildALBWhitelist()

        try:
            # Pront rules 
            for Rule,SGname,From,To in WhiteList:
                G(f"{SGname}  {Rule}  {From} - {To} ")
                
            print()
        except Exception as ERR:
            Err(ERR)


    elif args.Task == "elb":
        Y(f" Printing SG rules attached to ELB {args.lbname} using Profile={Profile}, Region={Region}")
        BuildELBWhitelist()

        # At this stage Whitelist contains all the rules.
        try:
            # Pront rules 
            for Rule,SGname,From,To in WhiteList:
                G(f"{SGname}  {Rule}  {From} - {To} ")
                
            print()
        except Exception as ERR:
            Err(ERR)

    elif args.Task == "albcheck":
        # CHeck specified IP whitelisted or not
        Y(f" INFO: Checking IP whitelisting on {args.lbname} using Profile={Profile}, Region={Region}. ")

        # Verify that provided IP are valid IPv4
        for IP in args.sourceip:
            ValidateIPV4(IP)

        # Call script to build list of Whitelists
        BuildALBWhitelist()

        # Now ready to validate each IP
        for IP in args.sourceip:
            TestIPWhitelist(IP)

    elif args.Task == "elbcheck":
        # CHeck specified IP whitelisted or not
        Y(f" INFO: Checking IP whitelisting on {args.lbname} using Profile={Profile}, Region={Region}. ")\
        # Verify that provided IP are valid IPv4
        for IP in args.sourceip:
            ValidateIPV4(IP)

        # Call script to build list of Whitelists
        BuildELBWhitelist()

        # Now ready to validate each IP
        for IP in args.sourceip:
            TestIPWhitelist(IP)




if __name__ == "__main__":
    main()