#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Boto3 create volume from snapshot
# Author:       Denny Vettom
# Dependencies: Python3, Boto3 library
# 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            03/10/2020     Initial Version                V 1.0

'''
Note : Using Boto3 resource not client
Using Boto3 to create a new volume from snapshot

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
    ec2resource = session.resource('ec2', region_name=Region)
except Exception as ERR:
    print (f" {ERR} \n ERROR: Failed to set ec2 client")
    exit()


def main():
    try:
        # Know snapshot name and instance zone. Create new disk from snapshot
        DestAZone = "eu-west-1"
        SNAP_ID = "snap-0206f7d853423841f"
        VolSize = "50"
        VolType = "gp2"


        # Create new Vol
        NewVol = ec2resource.create_volume(SnapshotId=SNAP_ID, AvailabilityZone=DestAZone, VolumeType=VolType, Size=int(VolSize))
        # If size not specified same size volume will be created
        print(" INFO : Waiting for volume to be created")
        
        waiter = ec2client.get_waiter('volume_available')
        waiter.wait(VolumeIds=[NewVol.id])

        # Once complete task finished.
        print (f" Info : Volume {NewVol.id} Created")

    except Exception as ERR:
        print(ERR)
        

    



if __name__ == "__main__":
    main()