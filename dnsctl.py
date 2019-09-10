#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Manage DNS tasks like DNA A, Alias, update, list, remove etc.
# Author:       Denny Vettom
# Dependencies: Aws cli with profile, boto3 and dvmodule.py, validators, socket
# https://github.com/vettom/Aws-Boto3 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            17/07/2019     FIrst ver add/update/delete record    V 1.0
# DV            10/09/2019     Fixed file input and error check.     V 1.1

import boto3, argparse, sys
# import dvmodule as dv #Custom module
import validators, socket

# Set Boto3 client
route53=boto3.client('route53')
"""
Add update or delete DNS entry. 
Define default ZoneID in variable if you are using same zone frequently.
Script checks and validates if provided arguments are valid IP or CNAME
If request is to add resource script will check for existing entry and exit if entry already exists.
Script will create alias record if destination is CNAME, and A record if IP provided.
"""
# Set a default value for Default Zone ID.
DEFZONEID = "Z2AYG8VDA7NG3D"

NOTE = "Script to manage DNS record in vettom.co.uk by default or provide -z zoneid to create in another zone."

# Use Arg Parse function to get input.
P = argparse.ArgumentParser(description='Manage routine DNS tasks.', epilog=NOTE)

# List last 10 snapshots for source hosts based on --src_device
P.add_argument('Task', choices=['add','update', 'delete'], help='Choose task toperform')

# Here mutually exclusive option to decide if it is IP, alias or list of aliases in file
group = P.add_mutually_exclusive_group(required=True)
# Arg1 and 2 are mutually exclusive
group.add_argument('-s', '--src_url' ,nargs='+' , help='Alias/Domain  name to be created separated by space')
group.add_argument('-f', '--src_file', help='File containing Alias list, one per line')

# Accepting regular arguments
P.add_argument('-d','--destination',  help='Destination CNAME or IP')
P.add_argument('-z','--zoneid', default=XXXXX, help='Zone ID, defaults to xxxx ID')
P.add_argument('--destzoneid', default=XXXXX, help='Destination Zone ID for ELB only or if different zoneid')
P.add_argument('--health_check', default=False, choices= ['True', 'False'] ,help='Evaluate health check, Default=False')


args = P.parse_args()

########## End of Arg Parse

def ValidateDom(Var):
    return validators.domain(Var)

def ValidateDNS(Var):
    # Test if DNS entry already resolves or not.
    try:
        socket.gethostbyname(Var)
        return True
    except:
        return False

def ValidateIP(IP):
    try:
        socket.inet_aton(IP)
        return True
    except:
        return False

def VerifyNoDNS(URL):
    # Verify Domain name is valid and no existing entry.  Exit in either case
    Result = validators.domain(URL)
    # Verify domain name is valid, if not exit

    if Result is not True:
        print (" ERROR: '{}' does not appear to be valid Domain name, please verify " .format(URL))
        exit()


    # Test and make sure DNS entry does not exists, if exist stop script 
    try:
        Output = socket.gethostbyname(URL)   #If successful domain resolved so exit 
        # Output = False
        return False
    except:
        return True

    
        


def VerifyDNSExists(URL):
    # Test URL for format also make sure exists.
    Result = validators.domain(URL)
    # Verify domain name is valid, if not exit
    if Result is not True:
        print (" ERROR: '{}' does not appear to be valid Domain name, please verify " .format(URL))
        exit()

    # Ensure URL can be resolved, if not exit
    try:
        Output = socket.gethostbyname(URL)
    except:
        print(" ERROR : '{}' failed to resolve, please verify URL is valid. " .format(URL) )
        exit()


def DNSAliasRecord(Var, Action):
# Creates Alias record
    try:
        response=route53.change_resource_record_sets(
            HostedZoneId=args.zoneid,
            ChangeBatch={
                'Comment': 'Creating a new Resource Record Set',
                       'Changes': [
                   {
                               'Action': Action,
                               'ResourceRecordSet': {
                             'Name': Var,
                             'Type': 'A',
                           'AliasTarget': {
                                           'HostedZoneId': args.zoneid,
                                           'DNSName': args.destination,
                                           'EvaluateTargetHealth': args.health_check
                                          },
                                                    }
                    },
                ]
                        }
        )
        # If Creation was success print success pessage
        print (" SUCESS : Action = '{}' Alias '{}' to '{}' completed" .format(Action, Var, args.destination ))
    except Exception as ERR:
        print (ERR, "\n ERROR : Action = '{}' Failed to create Alias '{}' Pointing to '{}' " .format(Action, Var, args.destination))


def DNSHostRecord(Var, Action):
# Creates Host entry to UP
    try:
        print ("Adding ", Var, Action, args.destination)
        response=route53.change_resource_record_sets(
            HostedZoneId=args.zoneid,
            ChangeBatch={
                'Comment': 'Creating a new Resource Record Set',
                       'Changes': [
                   {    
                               'Action': Action,
                               'ResourceRecordSet': {
                                 'Name': Var,
                                 'Type': 'A',
                                 'TTL' : 300,
                                 'ResourceRecords': [ {'Value': args.destination } ]
                                                    }
                    }
                ]
                        }
        )
        # If Creation was success print success pessage
        print (" SUCESS : Action = '{}' Host address '{}' to '{}' " .format(Action, Var, args.destination ))
    except Exception as ERR:
        print (ERR, "\n ERROR : Action = '{}' Failed to create Host '{}' Pointing to '{}' " .format(Action, Var, args.destination))

def VerifyDestinationpresent():
    # Simple check to ensure destination argument is provided.
    if args.destination is None:
        P.print_help()
        print (" ERROR: -d is required argument ")
        exit()


###########  End of Functions

def main():
    # Process arguments
    if args.Task == "add":
        '''
        In this section, first check if destination is IP or not, and select IP or Alias action based on that.
        Alias : Verify destination is valid, source URL are valid and does not already exist.
        '''
        Action = "CREATE"
        # Ensure destination argument is provided as it is not marked as required.
        VerifyDestinationpresent()

        # Check if the task is to add IP, or Alias and process 
        Result = ValidateIP(args.destination)    
        if Result is True:
            # A record creation
            for Alias in args.src_url:
                try:
                    #When creating entry ensure no entry exists already.
                    VerifyNoDNS(Alias)
                    DNSHostRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS creation failed and errors is '{}' " .format(ERR))

        else:
            # Here creating Alias record to a CNAME
            # execute based on -f or -s argument 

            # Verify destination is valid CNAME
            VerifyDNSExists(args.destination)

            if args.src_url:
            # Loop through all the Alias provided if provided as argument
                for Alias in args.src_url:
                    try:
                        #When creating entry ensure no entry exists already.
                        Result = VerifyNoDNS(Alias)
                        if Result is True:  
                            DNSAliasRecord(Alias, Action)
                        else:
                            print(" WARNING : '{}' already exists, use \'update\' to replace entry. " .format(Alias))
                    except Exception as ERR:
                        print (" ERROR: DNS creation failed and errors is '{}' " .format(ERR))

                exit()
            elif args.src_file :
                print (" INFO : Processing source file {} " .format(args.src_file))
                try:
                    FILE = open(args.src_file, "r")
                    LIST = FILE.readlines()
                    FILE.close()
                except Exception as ERR:
                    print ("Failed to open file {} " .format(args.src_file))

                # Now contents of file is available in List, process it.
                for Alias in LIST:
                    try:
                        Alias = Alias.rstrip("\n")
                        #When creating entry ensure no entry exists already.
                        Result = VerifyNoDNS(Alias)
                        if Result is True:  
                            DNSAliasRecord(Alias, Action)
                        else:
                            print(" WARNING : '{}' already exists, use \'update\' to replace entry. " .format(Alias))
                    except Exception as ERR:
                        print (" ERROR: DNS creation failed and errors is '{}' " .format(ERR))
                

                exit ()

    elif args.Task == "update":
        Action = "UPSERT"
        # Ensure destination argument is provided as it is not marked as required.
        VerifyDestinationpresent()

        # Check if the task is to add IP, or Alias and process 
        Result = ValidateIP(args.destination)    
        if Result is True:
            # A record creation
            for Alias in args.src_url:
                try:                    
                    DNSHostRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS update failed and errors is '{}' " .format(ERR))

        else:
            # Here creating Alias record to a CNAME

            # Verify destination is valid CNAME
            VerifyDNSExists(args.destination)

            # Loop through all the Alias provided
            for Alias in args.src_url:
                try:
                    DNSAliasRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS creation failed and errors is '{}' " .format(ERR))

    elif args.Task == "delete":
        Action = "DELETE"
        # Ensure destination argument is provided as it is not marked as required.
        VerifyDestinationpresent()

        # Check if the task is to add IP, or Alias and process 
        Result = ValidateIP(args.destination)    
        if Result is True:
            # A record creation
            for Alias in args.src_url:
                try:                    
                    DNSHostRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS update failed and errors is '{}' " .format(ERR))

        else:
            # Loop through all the Alias provided
            for Alias in args.src_url:
                try:
                    DNSAliasRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS deletion failed and errors is '{}' " .format(ERR))
    else:
        print("\n Sorry I did not get the options..")
        P.print_help()




if __name__ == "__main__":
    main()