# Python - Aws Boto3 Scripts
**Collection of Python3 scripts to manage AWS instance with help of Boto3. Scripts are written in self help mode.**
> scriptname -h for help
> All scripts expect AWS cli to be configured and at least one profile called default

### Scripts 
- dnsupdate.py               : Create DNS Alias record
- ec2instance.py             : Manage Ec2 instance stop/start
- elbctl.py                  : Mange Classig ELB 

# Script details

### dnsupdate.py
  Script can accept list of aliases or a list provided in a file. Zone ID is required, destzoneid required if destination alias in different DNS zone

``` 
usage: dnsupdate.py alias [-h] [-a ALIAS [ALIAS ...]] [-f SRC_FILE] -d
                          DEST_URL [-z ZONEID] [--destzoneid DESTZONEID]
                          [--health_check {True,False}]

optional arguments:
  -h, --help            show this help message and exit
  -a ALIAS [ALIAS ...], --alias ALIAS [ALIAS ...]
                        List of new alias to be created
  -f SRC_FILE, --src_file SRC_FILE
                        File containing Alias list, one per line
  -d DEST_URL, --dest_url DEST_URL
                        Name of destination of URL
  -z ZONEID, --zoneid ZONEID
                        Zone ID, defaults to adobecqms ID
  --destzoneid DESTZONEID
                        Destination Zone ID for ELB only or if different
                        zoneid
  --health_check {True,False} 
                        Evaluate health check, Default False 
```

Example of creating alias 123, abc.vettom.co.uk pointing to xyz.vettom.co.uk. Accept at command line or from file.

``` 
./dnsupdate.py alias -s 123.vettom.co.uk abc.vettom.co.uk -d zyz.vettom.co.uk -z ABCD 
./dnsupdate.py alias -f dns.txt -d zyz.vettom.co.uk -z ABCD
```

### elbctl.py
  Manage classic loadbalancer. List ELB in a VPC, status of ELB's, attach/detach instances
  > Script can accept multiple ELB, and instances, but all must be in same vpc. If multiple instances provided for attach/detach same action performed on all ELB names provided.

```
elbctl.py -h
usage: elbctl.py [-h] -a {list,status,attach,detach} [-p PROFILE] [-r REGION]
                 [--elb ELB [ELB ...]] [--vpc VPC [VPC ...]]
                 [-i INSTANCES [INSTANCES ...]]

ELB Operations tasks

optional arguments:
  -h, --help            show this help message and exit
  -a {list,status,attach,detach}, --action {list,status,attach,detach}
                        list/status/attach/detach
  -p PROFILE, --profile PROFILE
                        If no profile provided, assumes default
  -r REGION, --region REGION
                        Default is eu-west-1, or provide as argument
  --elb ELB [ELB ...]   Name/s of Aws ELB
  --vpc VPC [VPC ...]   Name/s of Aws VPC
  -i INSTANCES [INSTANCES ...], --instances INSTANCES [INSTANCES ...]
                        Instance ID/s
                        ```