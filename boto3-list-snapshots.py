#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Boto3 List snapshots by vol ID or by tag and printing information
# Author:       Denny Vettom
# Dependencies: Python3, Boto3 library
# 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            03/10/2020     Initial Version                V 1.0

'''
Using Boto3 to list snapshots if you know volume ID
Or listing snapshots with specific Key and value
printSnapshot function shows how to get necessary data out of result
'''
try:
    import boto3
except Exception as ERR:
    print(f' {ERR} \n  ERROR: Failed to import libraries requested, please ensure they are installed')
    exit()



# setting up to use profile called vettom and region eu-west-1
Profile = 'default'
Region = 'eu-west-1'
try:
    session = boto3.Session(profile_name=Profile)
    ec2client = session.client('ec2', region_name=Region)
except Exception as ERR:
    print (f" {ERR} \n ERROR: Failed to set ec2 client")
    exit()


# A funciton to print snapshot information
def printSnapshots(Snapshot):
    for X in Snapshot['Snapshots']:
        print(f"{X.get('SnapshotId')}, {X.get('VolumeId')}, {X.get('VolumeSize')}GB, {X.get('StartTime')}, {X.get('State')}")

def main():
    try:
        # Listing all snapshots for the volume if you know volume ID
        VolumeID = "vol-0893008f438c6c538"

        Result = ec2client.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [VolumeID, ]}, ], )
        # Print information from resulting Json
        printSnapshots(Result)

    except Exception as ERR:
        print(ERR)
        exit()


     # Finding all snapshots if you know it by tags
    try:
        TKey = "Name of the tag"
        TValue = "Value of the Key"
        Result = ec2client.describe_snapshots(Filters=[{'Name': 'tag:' + TKey, 'Values': [TValue ]}, ], ) 
        printSnapshots(Result)

    except Exception as ERR:
        print(ERR)
        exit()


if __name__ == "__main__":
    main()