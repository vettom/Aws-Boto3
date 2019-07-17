#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Manage DNS tasks like DNA A, Alias, update, list, remove etc.
# Author:       Denny Vettom
# Dependencies: Aws cli with profile, boto3 and dvmodule.py, validators, socket
# Improved version with sub menu and its own argument 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            17/07/2019     FIrst ver add/update/delete record    V 1.0

import boto3, argparse, sys
# import dvmodule as dv #Custom module
import validators, socket

# Set Boto3 client
route53=boto3.client('route53')
"""
Add remove or delete DNS entry. 
"""

NOTE = "Script to manage DNS record in adobecqms.net by default or provide -z zoneid to create in another zone."

# Use Arg Parse function to get input.
P = argparse.ArgumentParser(description='Manage routine snapshot tasks.', epilog=NOTE)

# List last 10 snapshots for source hosts based on --src_device
P.add_argument('Task', choices=['add','update', 'delete'], help='Choose task toperform')

# Here mutually exclusive option to decide if it is IP, alias or list of aliases in file
group = P.add_mutually_exclusive_group(required=True)
# Arg1 and 2 are mutually exclusive
group.add_argument('-s', '--src_url' ,nargs='+' , help='Alias/Domain  name to be created separated by space')
group.add_argument('-f', '--src_file', help='File containing Alias list, one per line')

# Accepting regular arguments
P.add_argument('-d','--destination',  help='Destination CNAME or IP')
P.add_argument('-z','--zoneid', default='ABCD', help='Zone ID, defaults to adobecqms ID')
P.add_argument('--destzoneid', default='ABCD', help='Destination Zone ID for ELB only or if different zoneid')
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
        Result = True
    except:
        return

    if Result is True:
        # print(" '{}' resolves to '{}' " .format(URL, Output))
        print(" ERROR : '{}' already exists, use \'update\' to replace entry. " .format(URL))
        exit()


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

            # Verify destination is valid CNAME
            VerifyDNSExists(args.destination)

            # Loop through all the Alias provided
            for Alias in args.src_url:
                try:
                    #When creating entry ensure no entry exists already.
                    VerifyNoDNS(Alias)
                    DNSAliasRecord(Alias, Action)
                except Exception as ERR:
                    print (" ERROR: DNS creation failed and errors is '{}' " .format(ERR))

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