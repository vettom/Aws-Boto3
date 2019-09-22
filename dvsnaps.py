#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Attch snapshot to another instance, list snapshots, mount as another device.
# Author:       Denny Vettom
# Dependencies: Custom MSCCMDB, Aws cli with profile, boto3 and dvmodule.py
# Improved version with sub menu and its own argument 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/02/2019     Initial Version in Py3             V 1.0
#
import boto3, time, re, sys, argparse
import datetime, dateutil
from dateutil import parser
import dvmodule as dv #Custom module
import dvclass 

"""
This script is designed to work with my custom CMDB created from MSC. Main purpose is to identify disk/snapshots and attach/detach
Clone : Get latest or based on specific date snapshot and attach to destination replacing disk specified in dest_disk
Copy : attach snapshot to dest with custom device name specified or xvdg
List  : List snapshots taken in past 10days. Option to specify date as well as device name.

"""
# Below is CMDB file, if does not exist, skip the task
LIST = "/Users/vettom/Scripts/Conf/mscallenv.txt"
global ec2resource, ec2client

Today = str(datetime.date.today())
NOTE = "Script requires CMDB with hosts detail. Scripts uses CMDB to speed up decition"
# Use Arg Parse function to get input.
P = argparse.ArgumentParser(description='Manage routine snapshot tasks.', epilog=NOTE)
# Add arguments that are required for all sub tasks

# P.add_argument('-p','--profile', default="default", help='Default profile=default')
# P.add_argument('--snap_id', help='Specify Snapshot ID if known, or latest snap of src_device used')
# P.add_argument('--src_device', default="/dev/xvdba", help='Disk Device name on Source host. Defaults to /dev/xvdba')
# P.add_argument('--start_date', default=Today, help='Defults to todays date or specify YYYY/MM/DD')


# Use sub parse to define optional arguments specific to task.
Sub = P.add_subparsers(title="Required arguments", dest="Task")

# List last 10 snapshots for source hosts based on --src_device
List = Sub.add_parser("list",help="List snapshots in last 10days or date specified")
List.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
List.add_argument('-p','--profile', default="default", help='Default profile=default')
List.add_argument('--snap_id', help='Specify Snapshot ID if known, or latest snap of src_device used')
List.add_argument('--src_device', default="/dev/xvdba", help='Disk Device name on Source host. Defaults to /dev/xvdba')
List.add_argument('--start_date', default=Today, help='Defults to todays date or specify YYYY/MM/DD')


# List volumes and size of volumes attached to Source Host
Vol = Sub.add_parser("listvol", help="List volume and size of volumes")
Vol.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
Vol.add_argument('-p','--profile', default="default", help='Default profile=default')

# Create a snapshot
Snapshot = Sub.add_parser("snap", help="Create snapshot of volume provided as argument")
Snapshot.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
Snapshot.add_argument('-v','--volume', help='Volume ID', required=True)
Snapshot.add_argument('-o','--owner', default="Vettom", help='Set to Vettom by defauly')
Snapshot.add_argument('-p','--profile', default="default", help='Default profile=default')
Snapshot.add_argument('-w','--wait', default=True, help='To skip waiting say no.')

# Used for replacing disk on destination host using snapshot from Source. Device can be specified but expect it to be valid at both ends
Clone = Sub.add_parser("clone", help="Attach snap of Source disk to Dest by replacing dest_device")
Clone.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
Clone.add_argument('-d','--dest_host', help='Destination Host. Required', required=True)
Clone.add_argument('--snap_id', help='Specify Snapshot ID or lates based on src_device will be used')
Clone.add_argument('--dest_device', default="/dev/xvdba", help='Disk Device name on Destination host. Defaults to /dev/xvdba')
Clone.add_argument('--voltype', default="standard", choices=['standard', 'gp2', 'sc1', 'st1'], help='Volume type to be created standard(default)/gp2/sc1/st1')
Clone.add_argument('-p','--profile', default="default", help='Default profile=default')
Clone.add_argument('--src_device', default="/dev/xvdba", help='Disk Device name on Source host. Defaults to /dev/xvdba')
Clone.add_argument('--start_date', default=Today, help='Defults to todays date or specify YYYY/MM/DD')

# Copy action attache disk to destination for parallel mount.
Copy = Sub.add_parser("copy", help="Attach snapshot of Source to destination for parallel mounting")
Copy.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
Copy.add_argument('-d','--dest_host', help='Destination Host. Required', required=True)
Copy.add_argument('--snap_id', help='Specify Snapshot ID or lates based on src_device will be used')
Copy.add_argument('--dest_device', default="/dev/sdg", help='Disk Device name on Destination host. Defaults to /dev/sdg')
Copy.add_argument('--voltype', default="gp2", choices=['standard', 'gp2', 'sc1', 'st1'], help='Volume type to be created standard/gp2(default)/sc1/st1')
Copy.add_argument('-p','--profile', default="default", help='Default profile=default')
Copy.add_argument('--src_device', default="/dev/xvdba", help='Disk Device name on Source host. Defaults to /dev/xvdba')
Copy.add_argument('--start_date', default=Today, help='Defults to todays date or specify YYYY/MM/DD')

# Remove and delete unused volume from Source host based on  --src_device
Rmvol = Sub.add_parser("rmvol",help="Detach and remove unused volume")
Rmvol.add_argument('-s','--src_host', help='Source Hostname must be specified', required=True)
Rmvol.add_argument('-p','--profile', default="default", help='Default profile=default')
Rmvol.add_argument('--src_device', default="/dev/sdg", help='Disk Device name on Source host. Defaults to /dev/sdg')

args = P.parse_args()

#  ---------------- End of Argument Parsing.  ---------------- 

def GetVolume(instance_id, Region, Profile, Device, Hostname):
    # Get volume ID for the device specified
    try:
        ec2resource = dv.SetEC2Resource(Profile, Region)
        instance = ec2resource.Instance(instance_id)
        # Count number of devices if more than 2, expecting sda1 and xvdba
        if len(instance.block_device_mappings) > 2:
            print (" WARNING : More than 2 disks found, using ",  Device)

        for device in instance.block_device_mappings:
            if device.get('DeviceName') == Device:
                volume = device.get('Ebs')
                VolID = volume.get('VolumeId')
                DevID = device.get('DeviceName')
                print (" INFO : ", Hostname, " VolumeID :" , VolID , " Device :" , DevID)
                return VolID, DevID
    except Exception as ERR:
        print (" ERROR : Failed to get Volume information, please verify correct Profile, Hostname provided")
        print( " ERROR : {}" .format(ERR))
        exit(1)


def PrintSnaps(Snapshot):
    # Simply print snapshot details including the start time and state.
    try:
        DateLimit= parser.parse(args.start_date).date() - datetime.timedelta(days=10)
        # Process Snapshot list
        print("\n  Snapshots 10 days from ", args.start_date)
        for X in Snapshot['Snapshots']:
            if X.get('State') == "completed":
                Snapdate = str(X.get('StartTime'))
                # Show snapshots in between specified/today -10 days
                if parser.parse(Snapdate).date() >= DateLimit and parser.parse(Snapdate).date() <=  parser.parse(args.start_date).date():
                    SNAP = X.get('SnapshotId')
                    print (SNAP, X.get('StartTime'), X.get('State'))
            elif X.get('State') == "pending":
                Snapdate = str(X.get('StartTime'))
                SNAP = X.get('SnapshotId')
                print (SNAP, X.get('StartTime'), X.get('State'), X.get('Progress'))
            else:
                print (" ERROR: No Snapshots found!")
    except Exception as ERR:
        print (ERR)
        print (" ERROR : Failed to list Snapshots")


def listsnapshots(VolumeID, Region, Profile):
    # This gets list of snapshots are return to function for processing.
    try:
        ec2client = dv.SetEC2Client(Profile, Region)
        Result = ec2client.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [VolumeID, ]}, ], )
        return Result
    except exception as ERR:
        print (ERR)
        print (" ERROR : Failed to list Snapshot, please verify arguments like profile, host, disk etc")
        exit(1)


def GetLatestSnap(Snapshot):
    try:
        DateLimit= parser.parse(args.start_date).date() - datetime.timedelta(days=10)
        # Process Snapshot list and select latest based on date
        for X in Snapshot['Snapshots']:
            if X.get('State') == "completed":
                Snapdate = str(X.get('StartTime'))
                if parser.parse(Snapdate).date() >= DateLimit and parser.parse(Snapdate).date() <=  parser.parse(args.start_date).date():
                    SNAP = X.get('SnapshotId')
                    print (" INFO : Selected Snapshot ", SNAP, X.get('StartTime'))
                    return SNAP
            else:
                print (" ERROR: No Snapshots found ")
    except Exception as ERR:
        print (ERR)
        print (" ERROR : Failed to get latest Snapshot information.")
        exit(1)


def TestVar(Var):
    # Accept a variable name as argument and exit if not defined
    try:
        Var
    except NameError:
        print (" ERROR : Variable " , Var , "Not Defined ")
        return False
        exit(1)
    # Handle if variable initialised but no value set
    if Var is None:
        print (" Error : None Value set for variable " , Var)
        exit(1)

def StartInstance(Instance, Profile, Region):
    try:
        print (" INFO : Starting Instance " , Instance)
        ec2client = dv.SetEC2Client(Profile, Region)
        ec2client.start_instances(InstanceIds=[Instance])
        waiter = ec2client.get_waiter('system_status_ok')
        waiter.wait(InstanceIds=[Instance])
        print (" INFO : Instance " + Instance , " is Ready")
    except Exception as ERR:
        print (" ERROR : Failed to start instance " , Instance)
        print(" ", ERR)


def StopInstance(Instance, Profile, Region):
    try:
        print (" INFO : Stoppign instance " , Instance)
        ec2client = dv.SetEC2Client(Profile, Region)
        ec2client.stop_instances(InstanceIds=[Instance])
        waiter = ec2client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[Instance])
        print (" INFO : Instance " , Instance , " Stopped")
    except Exception as ERR:
        print (" ERROR : Failed to Stop instance " , Instance)
        print(" ", ERR)
        exit(1)

def CheckDeviceExist(instance_id, Region, Profile, Device, Hostname):
    # Function to check if the device already exist on the instance or not.
    try:
        ec2resource = dv.SetEC2Resource(Profile, Region)
        instance = ec2resource.Instance(instance_id)
        # Check all block devices and if matching return True
        for device in instance.block_device_mappings:
            if device.get('DeviceName') == Device:
                return True
                exit()
        # If none matched return False to indicate disk not found.
        return False        
    except Exception as ERR:
        print (" ERROR : Failed to get Volume information, please verify, Profile, Hostname etc are correct")
        print(" ", ERR)
        exit(1)


def ListVolume(instance_id, Region, Profile):
    try:
        try:
            # Generate list of volumes attached to the instance
            ec2resource = dv.SetEC2Resource(Profile, Region)
            instance = ec2resource.Instance(instance_id)
        except Exception as ERR:
            print(" ERROR : Failed to find instance using Profile={}, Region={}. Please check Profile/Region/Hostname" .format(Profile, Region))
            print(" ", ERR)
            exit()
        # Initialise Volumes variable to store ist of Volumes
        Volumes = []
        # Get list of volumes attached to Instance.
        for device in instance.block_device_mappings:
            Ebs = device.get('Ebs')
            Volumes.append(Ebs.get('VolumeId'))

        # List of Volumes are available as list in Volumes.Volume
        # Set Client for describing volume
        ec2client = dv.SetEC2Client(Profile, Region)
        # Loop through Volumes and print information
        for X in Volumes:
            Y = ec2client.describe_volumes(VolumeIds=[X])
            # Loop through the Volume information provided by above commad.
            for Z in Y['Volumes']:
                # Device name is saved in a different list
                for D in Z['Attachments']:
                    Dev = D['Device']

                print (Z['VolumeId'], Z['Size'], "GB ", Dev, Z['VolumeType'])
    except Exception as ERR:
        print ( " ERROR : Failed to get Volume information, please verify Profile, Region, Hostname etc are correct.")
        print(" ", ERR)
        exit(1)


def CreateSnapshot(Region,Vol):
    # Setting some Default variables, this will be added to snapshot Tags by default
    backup_type = "On Demand"
    Comments = "Snapshot created in AWS, not visible in MSC"
    StartTime = time.strftime('%Y-%m-%dT%H:%M:%S %Z')



    try:
        # Set EC2 variable with region, defaults to eu-west-1
        ec2client = boto3.SetEC2Resource(Profile, Region)
    except Exception as ERR:
        print (" ERROR : Failed to set EC2Resourece with arguments Profile={}, Region={}, Volume={}. \n Error is {} " .format(Profile,Region,Vol,ERR))
        exit()
   
    try:
        # Create snapshot of the volume
        snapshot = ec2client.create_snapshot(VolumeId=Vol, Description=args.src_host)
        # Add tags to snapshot created.
        snapshot.create_tags(Resources=[snapshot.id], Tags=[{'Key': 'Name', 'Value': args.src_host},
                                                            {'Key': 'InstanceID', 'Value': args.src_host},
                                                            {'Key': 'Type', 'Value': backup_type},
                                                            {'Key': 'Comments', 'Value': Comments},
                                                            {'Key': 'Owner', 'Value': args.owner}
                                                            ])

        # Print snapshot start message
        print (" INFO : Starting backup of volume {} at " .format(Vol, StartTime))
        print (" INFO : Snapshot ID is {} " .format(snapshot.id))
    except Exception as ERR:
        print (" ERROR: Failed to trigger backup with arguments Profile={}, Region={}, Volume={}. \n Error is {} " .format(Profile,Region,Vol,ERR))
        exit()
    
    # Check if need to wait for snapshot to complete
    if args.wait is not True:
        print (" INFO : Backup triggered for Volume {},  SnapID={}, please check progress separately. " .format(Vol,snapshot.id))
    else:
        # Wait for Snapshot status to be complete
        snapshot.load()
        while snapshot.state != 'completed':
            print (" INFO : Snapshot Progress {} {}" .format(snapshot.state, snapshot.progress))
            time.sleep(60)
            snapshot.load()
        else:
            Endtime = time.strftime('%Y-%m-%dT%H:%M:%S %Z')
            print (" INFO : Finished backup of volume {} at {}" .format(args.src_host, Endtime ))
            print (" INFO : SnapshotID is {}" .format(snapshot.id))


#  ---------------- End of Functions  ---------------- 
# --------------------------------------------------------------------------------------

def main():
    # ----- StartParsing the options if no arguments print help and exit.
    if args.Task is None:
        P.print_help()
        exit()

    global Profile
    Profile = args.profile
    global boto3
    global ams
    boto3 = dvclass.AWSBoto3()
    ams = dvclass.AMSCMDB()
# ----- First section ensuring CMDB file and able to find Instance details.
    # Try to open CMDB file, if faild stop execution.
    try:
        FILE = open(LIST, "r")
        Lines = FILE.readlines()
        FILE.close()
    except Exception as ERR:
        print(ERR)
        print ("ERROR : Failed to open File List ", LIST)
        exit(1)

    # Below command gets instance detals for the host from local file.
    # If Source instance not found stop execution
    try:
        result = dv.GetInstanceDetails(args.src_host, Lines)
        Region = result[0]
        instance_id = result[1]
    except Exception as ERR:
        print (ERR)
        print (" ERROR : Instance details not found in local file ",  LIST)
        exit(1)


# ------ Task for list option.
    if args.Task == "list":
        try:
            print (" INFO : Using Profile : ", args.profile)
            Result = GetVolume(instance_id, Region, Profile, args.src_device, args.src_host)
            # result returns Volume and Device Name
            VolumeID = Result[0]
            DeviceID = Result[1]
        except:
            print (" ERROR : Failed to volume information")
            exit(1)

        Snapshot = listsnapshots(VolumeID, Region, Profile)
        PrintSnaps(Snapshot)
        exit()
# ---- End of list Snaps

    elif args.Task == "listvol":
        # List volumes attached to Source Host specified.
        print (" INFO : Listing volumes for ", args.src_host, Region, "\n")
        Result = ListVolume(instance_id, Region, args.profile)
        # result returns Volume and Device Name
        # VolumeID = Result[0]
        # DeviceID = Result[1]
#----- End of list volumes

    elif args.Task == "clone":
#-----Start of Clone. Source instance details already available
        try:
            # Get Destination host id and region.
            result = dv.GetInstanceDetails(args.dest_host, Lines)
            DestRegion = result[0]
            Destinstance_id = result[1]
            DestAZone = result[2]
        except Exception as ERR:
            print(ERR)
            print (" ERROR : ", args.dest_host, " Not found in CMDB")
            exit(1)

        # If snap_id not provided, use the default latest or prompt
        if args.snap_id is None:
            # Identify Disk information for Source Host
            Result = GetVolume(instance_id, Region, Profile, args.src_device, args.src_host)
            # result returns Volume and Device Name
            VolumeID = Result[0]
            DeviceID = Result[1]
            # List Snapshots and select latest by default
            Snapshot = listsnapshots(VolumeID, Region, Profile)
            SNAP_ID = GetLatestSnap(Snapshot)
        else:
            SNAP_ID = args.snap_id

        try:
            # Identify Destination device to be detached, have DestInstance ID and region.
            Result = GetVolume(Destinstance_id, DestRegion, Profile, args.dest_device, args.dest_host )
            # result returns Volume and Device Name
            DestVolumeID = Result[0]
            DestDeviceID = Result[1]
        except Exception as ERR:
            print (ERR)
            print(" ERROR : Failed to Destination instance volume information")
            exit(1)

        # Verify each variable have a value
        for VAR in ["VolumeID", "DeviceID", "DestVolumeID", "DestDeviceID", "SNAP_ID"]:
            TestVar(VAR) 
        # Promp t confirmation
        print ("\n INFO : Following information found for processing")
        print ("  Source      :", args.src_host , " Snapshot ID :" , SNAP_ID )
        print ("  Destination :", args.dest_host," Dest Details :", DestVolumeID, DestDeviceID, DestAZone )

        # Create new volume with Dest Region and matching type
        Respose = input("\n Proceed ? y/n :")
        if Respose == "y":

            # Shutdown Dest Host, Detach diskand delete
            StopInstance(Destinstance_id, Profile, Region)
            print ( " INFO :", args.dest_host , " Stopped, detaching volume")
            # Set Boto3 resource for handling device.
            ec2resource = dv.SetEC2Resource(Profile, Region)
            ec2client = dv.SetEC2Client(Profile, Region)
            # Detach the volume and delete disk
            volume = ec2resource.Volume(DestVolumeID)
            try:
                # Detach volume from the Instance and delete Volum.
                volume.detach_from_instance(InstanceId=Destinstance_id, Force=True)
                waiter = ec2client.get_waiter('volume_available')
                waiter.wait(VolumeIds=[DestVolumeID],)
                print (" INFO : Volume Detached")
                volume.delete()
                print (" INFO : Volume Deleted")
            except Exception as ERR:
                print(ERR)
                print (" ERROR : Failed to remove Volume from " , args.dest_host, DestVolumeID)
                exit(1)

            # Create new volume from snapshot

            try:
                print (" INFO : Creating Volume from Snapshot" , SNAP_ID, DestAZone, args.voltype)
                NewVol = ec2resource.create_volume(SnapshotId=SNAP_ID, AvailabilityZone=DestAZone, VolumeType=args.voltype)
                waiter = ec2client.get_waiter('volume_available')
                waiter.wait(VolumeIds=[NewVol.id])
                print (" INFO : New Volume " , NewVol.id , " Created from " + SNAP_ID , " and is Available")
            except Exception as ERR:
                print (ERR, " ERROR : Failed to create Volume from Snap")
                exit(1)

            # Attach new vol and start instance.
            try:
                print (" INFO : Attaching Volume to Instance :" , args.dest_device, Destinstance_id, NewVol.id)
                ec2client.attach_volume(InstanceId=Destinstance_id, VolumeId=NewVol.id, Device=args.dest_device)
                # ec2.Instance(Destinstance_id).attach_volume(VolumeId=NewVol, Device=args.dest_device)
            except Exception as ERR:
                print (ERR, " ERROR : Faild to attach Volume to instance")
                exit(1)
            # Start the Dest instance
            StartInstance(Destinstance_id, Profile, Region)

            exit(0)
        else:
            print (" ERROR : Aborting activity")
            exit(1)
#-----End of Clone
        
    elif args.Task == "copy":
#-----
        try:
            # Get Destination host id and region.
            result = dv.GetInstanceDetails(args.dest_host, Lines)
            DestRegion = result[0]
            Destinstance_id = result[1]
            DestAZone = result[2]
        except Exception as ERR:
            print(ERR)
            print (" ERROR : ", args.dest_host, " Not found in CMDB")
            exit(1)

        # If snap_id not provided, use latest snapshot of device src_device
        if args.snap_id is None:
            # If Snapshot ID not provided, use src_device to get latest snapshot and use it.
            try:
                # Identify Disk information for Source Host. This can be used to find latest snapshot.
                Result = GetVolume(instance_id, Region, Profile, args.src_device, args.src_host )
                # result returns Volume and Device Name
                VolumeID = Result[0]
                DeviceID = Result[1]
            except Exception as ERR:
                print(ERR)
                print(" ERROR : Unable to get Snapshot for", args.src_host)
                exit(1)
                # List Snapshots and select latest by default
            Snapshot = listsnapshots(VolumeID, Region, Profile)
            SNAP_ID = GetLatestSnap(Snapshot)
        else:
            SNAP_ID = args.snap_id

        # At this stage must have ID of Snapshot to be used
        for VAR in ["SNAP_ID"]:
            TestVar(VAR)
        # Test to ensure that destination device does not exist. 
        Check = CheckDeviceExist(Destinstance_id, Region, Profile, args.dest_device, args.dest_host)
        if Check == True:
            print("\n ERROR : ", args.dest_device, " exist on ", args.dest_host, " Please remove disk and try  \n" )
            exit(1)
        else:
            print(" INFO : Dest Device name ", args.dest_device, "is available on " , args.dest_host )

        # Prompt confirmation
        print (" INFO : Following information found for processing")
        print (" Source      :", args.src_host, " Snapshot ID :" , SNAP_ID)
        print (" Destination : ", args.dest_host, " Dest AZ :",DestAZone," Dest Device:",args.dest_device)

        # Create new volume with Dest Region and matching type
        Respose = input("\n Proceed ? y/n :")
        if Respose == "y":

            # Create new volume from snapshot

            try:
                # Set Boto3 resource for handling device.
                ec2resource = dv.SetEC2Resource(Profile, Region)
                print (" INFO : Creating Volume from Snapshot " , SNAP_ID, DestAZone, args.voltype)
                NewVol = ec2resource.create_volume(SnapshotId=SNAP_ID, AvailabilityZone=DestAZone, VolumeType=args.voltype)
                ec2client = dv.SetEC2Client(Profile, Region)
                waiter = ec2client.get_waiter('volume_available')
                waiter.wait(VolumeIds=[NewVol.id])
                print (" INFO : New Volume " , NewVol.id , "Created from " , SNAP_ID , " and is Available")
            except:
                print (" ERROR : Failed to create Volume from Snap")
                # print NewVol, SNAP_ID, Destinstance_id
                exit(1)

            # Attach new vol and start instance.
            try:
                print (" INFO : Attaching Volume to Instance" , args.dest_host, Destinstance_id, args.dest_device, NewVol.id)
                ec2client.attach_volume(InstanceId=Destinstance_id, VolumeId=NewVol.id, Device=args.dest_device)
                print("\n SUCCESS : Disk attached to ", args.dest_host, " Device:", args.dest_device, " \n")
            except Exception as ERR:
                print ( ERR , "\n ERROR : Faild to attach Volume to instance", args.dest_host)
                exit(1)

            exit(0)

#-----
    elif args.Task == "rmvol":
        # Tasks for removing and deleting unused volume
        # Ensure disk is unmounted and not in use by OS.
        Check = CheckDeviceExist(instance_id, Region, Profile, args.src_device, args.src_host)
        if Check == True:
            try:
            # Identify Disk information for Source Host. This can be used to find latest snapshot.
                Result = GetVolume(instance_id, Region, Profile, args.src_device, args.src_host )
                # result returns Volume and Device Name
                VolumeID = Result[0]
                DeviceID = Result[1]
            except Exception as ERR:
                print(ERR)
                print(" ERROR : Unable to get Volume ID for", args.src_host)
                exit(1)

            print("\n  ----------------------------------------------------")
            print("   Please ensure disk unmounted and VG removed on Host")
            print("  ----------------------------------------------------")
            print("\n WARN : Detach and delete volume ", args.src_device, VolumeID, " from ", args.src_host, "?  \n" )
            Respose = input("\n Proceed ? y/n :")
            
            if Respose == "y":
                 # Set Boto3 resource for handling device.
                ec2resource = dv.SetEC2Resource(Profile, Region)
                ec2client = dv.SetEC2Client(Profile, Region)
                # Get Volume ID

                # Detach the volume and delete disk
                volume = ec2resource.Volume(VolumeID)
                try:
                    # Detach volume from the Instance and delete Volum.
                    volume.detach_from_instance(InstanceId=instance_id, Force=True)
                    waiter = ec2client.get_waiter('volume_available')
                    waiter.wait(VolumeIds=[VolumeID],)
                    print (" INFO : Volume Detached, deleting unused volume")
                    volume.delete()
                    print (" INFO : Volume Deleted")
                except Exception as ERR:
                    print(ERR)
                    print (" ERROR : Failed to remove Volume from " , args.dest_host, DestVolumeID)
                    exit(1)
                
        else:
            print("\n ERROR : Dest Device name ", args.src_device, " not found on " , args.src_host )

    elif args.Task == "snap":
        # Get  region info and pass to function.
        Result = ams.GetInstAWS(args.src_host)
        Region = Result[2]
        # Now ready to trigger Snapshot
        CreateSnapshot(Region, args.volume)


    else:
        print("\n Sorry I did not get the options.. :(")


if __name__ == "__main__":
    main()