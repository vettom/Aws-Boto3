#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Purpose : Create necessary DNS alias records. Specially designed for Barclays which requests alias creations.
# Author:       Denny Vettom
# Dependencies: Aws cli with profile, boto3, validators, socket
# Improved version with sub menu and its own argument 
# ----------------------------------------------------------------------------
# Name          Date            Comment                         Version
# ----------------------------------------------------------------------------
# DV            20/02/2019     FIrst ver with alias record              V 1.0

import boto3, argparse
import validators, socket

# Set Boto3 client
route53=boto3.client('route53')
"""
Script to manage DNS entries, create/delete/update
Alias : Create alias, input as a list in file or multy entry at command line. Does verify before creating.

"""


NOTE = "Script to create alias record in adobecqms.net by default"

# Use Arg Parse function to get input.
P = argparse.ArgumentParser(description='Manage routine snapshot tasks.', epilog=NOTE)
# Use sub parse to define optional arguments specific to task.
Sub = P.add_subparsers(title="Required arguments", dest="Task")

# List last 10 snapshots for source hosts based on --src_device
Alias = Sub.add_parser("alias",help="Create new alias record to a CNAME")
Alias.add_argument('-a','--alias', nargs='+', help='List of new alias to be created')
Alias.add_argument('-f', '--src_file',  help='File containing Alias list, one per line')
Alias.add_argument('-d','--dest_url', help='Name of destination of URL', required=True)
Alias.add_argument('-z','--zoneid', default='ABCD', help='Zone ID, defaults to adobecqms ID')
Alias.add_argument('--destzoneid', default='ABCD', help='Destination Zone ID for ELB only or if different zoneid')
Alias.add_argument('--health_check', default=False, choices= ['True', 'False'] ,help='Evaluate health check, Default False')

args = P.parse_args()

def ValidateDom(Var):
    return validators.domain(Var)

def ValidateDNS(Var):
    # Test if DNS entry already resolves or not.
    try:
        socket.gethostbyname(Var)
        return True
    except:
        return False

def CreateRecord(Var):
# Creates Alias record
    try:
        response=route53.change_resource_record_sets(
            HostedZoneId=args.zoneid,
            ChangeBatch={
                'Comment': 'Creating a new Resource Record Set',
                       'Changes': [
                   {
                               'Action': 'CREATE',
                               'ResourceRecordSet': {
                             'Name': Var,
                             'Type': 'A',
                           'AliasTarget': {
                                           'HostedZoneId': args.zoneid,
                                           'DNSName': args.dest_url,
                                           'EvaluateTargetHealth': args.health_check
                                          },
                                                    }
                    },
                ]
                        }
        )

        # If Creation was success print success pessage
        print (" SUCESS : Alias '{}' to '{}' created" .format(Var, args.dest_url ))
    except Exception as ERR:
        print (ERR, "\n ERROR :Failed to create Alias '{}' Pointing to '{}' " .format(Var, args.dest_url))

#  ---------------- End of Functions  ---------------- 

def main():
    # ----- StartParsing the options if no arguments print help and exit.
    if args.Task is None:
        P.print_help()
        exit()

    # alias and src_file is mutually exclusive
    if args.alias and args.src_file is not None: 
        print("\n ERROR : Please provide either alias or src_file, not both\n")
        exit()



# ----- Start main action processing based of arguments

    if args.Task == "alias":

    # Decide process file or just arguments
        if args.src_file is not None:
            # Process entries in file
            try:
                FILE = open(args.src_file, "r")
                Lines = FILE.readlines()
                FILE.close()
                # Now process each line validate and create alias
                for Line in Lines:
                    Alias = '{}'.format(Line).rstrip()
                    # Validate that entry is in valid domain format
                    Result = ValidateDom(Alias)
                    if Result is True:
                        # Now verify DNS entry does not exist alreasy
                        ANS = ValidateDNS(Alias)
                        if ANS is False:
                            CreateRecord(Alias)
                        else:
                            print (" WARNING : Alias '{}' already exists, skipping creation" .format(Alias))
                    else:
                        print("\n ERROR : '{}' failed Domain name validation" .format(Alias))
            except Exception as ERR:
                print(ERR, "\n ERROR : Failed to open", args.src_file)
                exit()
        
        elif args.alias is not None:
            # Process Alias provided at command line
            for Alias in args.alias:
                Result = ValidateDom(Alias)
                if Result is True:
                    Result = ValidateDom(Alias)
                    if Result is True:
                        # Now verify DNS entry does not exist alreasy
                        ANS = ValidateDNS(Alias)
                        if ANS is False:
                            CreateRecord(Alias)
                        else:
                            print (" WARNING : Alias '{}' already exists, skipping creation" .format(Alias))
                    
            exit()
    else:
        print(" I do not support that argument")
        exit()


if __name__ == "__main__":
    main()
