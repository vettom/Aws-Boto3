#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Boto3 Authentication using AWS CLI profiles
# Author:       Denny Vettom
# Dependencies: Python3, Boto3 library
# 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            02/10/2020     Initial Version                V 1.0

'''
Demonstration of how to use AWS cli profile authentication in Boto3 and set ec2 client.
Uses boto3 session to set profile to be used.
Argparse used to validate arguments
'''
try:
    import boto3
except Exception as ERR:
    print(f' {ERR} \n  ERROR: Failed to import libraries requested, please ensure they are installed')
    exit()



# setting up to use profile called vettom and region eu-west-1
Profile = 'vettom'
Region = 'eu-west-1'
try:
    session = boto3.Session(profile_name=Profile)
    ec2client = session.client('ec2', region_name=Region)
except Exception as ERR:
    print (f" {ERR} \n ERROR: Failed to set ec2 client")
    exit()