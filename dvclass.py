#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Class file to manage ams CMDB and other common ec2 tasks
# Author:       Denny Vettom
# Dependencies: PYTHON -3, Boto3,  profiles
#
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            07/09/2019     Initial Version                  V 1.0
# DV            09/01/2020     Addinng ELBV2 in boto3           V 1.0
#  CMDB Format as below
#   0          1    2.        3.     4.    5.   6.      7.      8.  9. 10.     11   
#  Topology  ExtIP INT_IP Hostname Region VPC InstID Insttype Size AZ TopoID Cloud

import re,os,sys,boto3



class AMSCMDB:
    def __init__(self):
        global SCR_HOME
        global Conf
        # Load the configuration file and store in Variable called CMDB
        SCR_HOME = os.path.dirname(os.path.realpath(__file__))
        Conf = SCR_HOME + "/mscallenv.txt"
        try:
            global CMDB
            FILE = open(Conf, "r")
            CMDB = FILE.readlines()
            FILE.close()
        except:
            print (" ERROR : Failed to open CMDB file ", Conf)
            exit ()

    def GetHostname(self, ARG):
        # find and return instance ID from the CMDB
        try:
        # Get Instance ID or Hostname as argument and return InstanceID and Hostname
            for Line in CMDB:   
                if (re.search('\s%s\s' % ARG, Line)):
                    if (re.search('\sAWS\s', Line)):
                        Var = Line.split()
                        # Region = Var[4]
                        # instance_id = Var[6]
                        # AZ = Var[9]
                        Host = Var[3]
                        return  Host
        except Exception as ERR:
            print(ERR)
            print (" ERROR : Failed to get instance details, please verify custom environment file is present and upto date")
            exit(1)

    def GetInstID(self, ARG):
        # find and return instance ID from the CMDB
        try:
        # Get Instance ID or Hostname as argument and return InstanceID and Hostname
            for Line in CMDB:
                if (re.search('\s%s\s' % ARG, Line)):
                    if (re.search('\sAWS\s', Line)):
                        Var = Line.split()
                        # Region = Var[4]
                        instance_id = Var[6]
                        # AZ = Var[9]
                        Host = Var[3]
                        return instance_id
        except Exception as ERR:
            print(ERR)
            print (" ERROR : Failed to get instance details, please verify custom environment file is present and upto date")
            exit(1)

    def GetInstAWS(self, ARG):
        # Get Instance ID or Hostname as argument, and return Instance_ID, Host,  Region, AZone, VPC
        try:
        # Find the instance from file and ger region and instance ID
            for Line in CMDB:
                if (re.search('\s%s\s' % ARG, Line)):
                    if (re.search('\sAWS\s', Line)):
                        Var = Line.split()
                        Region = Var[4]
                        instance_id = Var[6]
                        AZ = Var[9]
                        Host = Var[3]
                        VPC = Var[5]
                        return instance_id, Host, Region, AZ, VPC
        except Exception as ERR:
            print(ERR)
            print (" ERROR : Failed to get instance details, please verify custom environment file is present and upto date")
            exit(1)


    def GetVpcReg(self, ARG):
        # Accept Topology as argument and return VPC and region as a list.
        # Since there can be multiple VPC, result returned as a list.
        try:
        # Find the instance from file and ger region and instance ID
            LIST = []
            for Line in CMDB:
                # if (re.search('\s%s\s' % ARG, Line)):
                if (re.search('^%s\s' % ARG, Line)):
                    if (re.search('\sAWS\s', Line)):
                        Var = Line.split()
                        Region = Var[4]
                        VPC = Var[5]
                        # print("{} {}" .format(Region, VPC))
                        LIST.append("{} {}" .format(VPC, Region))
                # else:
                #     LIST =  False
        except Exception as ERR:
            print(ERR)
            print (" ERROR : Failed to get Topology details, please verify custom environment file is present and upto date")
            exit(1)
        return (set(LIST))




class AWSBoto3:
    def __init__(self):
        global ec2client
        global ec2resource

    def test(ARG):
        print ("Test class executed received ", ARG)

    def SetEC2Client(self, Profile, Region):
        global ec2client
        # Sets ec2 client with profile and Region.
        print ("Client in class")
        session = boto3.Session(profile_name=Profile)
        ec2client = session.client('ec2', region_name=Region)
        # return ec2client


    def SetEC2Resource(self, Profile, Region):
        # Sets ec2 client with profile and Region.
        global ec2resource
        session = boto3.Session(profile_name=Profile)
        ec2resource = session.resource('ec2', region_name=Region)
        return ec2resource

    def SetELBClient(self, Prof, Reg):
        try:
            # Sets elb client with profile and Region. Depending on the Boto3 funciton use client or resource.
            session = boto3.Session(profile_name=Prof)
            # Set client for Classic Loadbalancer.
            ec2client = session.client('elb', region_name=Reg)
            return ec2client
        except Exception as ERR:
            print (" ERROR : Failed to set ec2client, please ensure arguments are passed. \n {}" .format(ERR))
            print(ERR)
            exit(1)
    
    def SetALBClient(self, Prof, Reg):
        try:
            # Sets elb client with profile and Region. Depending on the Boto3 funciton use client or resource.
            session = boto3.Session(profile_name=Prof)
            # Set client for Classic Loadbalancer.
            ec2client = session.client('elbv2', region_name=Reg)
            return ec2client
        except Exception as ERR:
            print (" ERROR : Failed to set ec2client, please ensure arguments are passed. \n {}" .format(ERR))
            sys.exit(1)


