#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Boto3 get volume info from instance, detach and delete
# Author:       Denny Vettom
# Dependencies: Python3, Boto3 library
# 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            02/10/2020     Initial Version                V 1.0

'''
Using Boto3 to get list of disks from instance.
Detach disk and remove detached disk
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
    # ec2client = session.client('ec2', region_name=Region)
    ec2resource = session.resource('ec2', region_name=Region)
except Exception as ERR:
    print (f" {ERR} \n ERROR: Failed to set ec2 client")
    exit()


def main():
    InstanceID = "i-0c9f5627014e1b7"
    try:
        # Using Boto3 resource to get list of disks
        Instance = ec2resource.Instance(InstanceID)

        # Process output to get list of all disks
        for device in Instance.block_device_mappings:
            
            volume = device.get('Ebs')
            VolID = volume.get('VolumeId')
            DevID = device.get('DeviceName')
            print (" VolumeID :" , VolID , " Device :" , DevID)

    except Exception as ERR:
        print(ERR)
        exit()
       


    # Detaching a Volume 
    try:
        VolumeID = "vol-0e9493a59"

        volume = ec2resource.Volume()
        volume.detach_from_instance(InstanceId=InstanceID, Force=True)
        waiter = ec2client.get_waiter('volume_available')
        waiter.wait(VolumeIds=[VolumeID],)
        print (" INFO : Volume Detached")

        # Deleting Volume Device details already available
        volume.delete()
        print (" INFO : Volume Deleted")


    except Exception as ERR:
        print(ERR)
        exit()

if __name__ == "__main__":
    main()