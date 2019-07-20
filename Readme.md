# Python - Aws Boto3 Scripts ![alt text](https://vettom.github.io/images/Robin2cm.png "Denny Vettom Logo")
**Collection of Python3 scripts to manage AWS instance with help of Boto3. Scripts are written in self help mode.**
> scriptname -h for help
> All scripts expect AWS cli to be configured and at least one profile called default




### Scripts 
- [dnsctl.py](https://github.com/vettom/Aws-Boto3#dnsupdatepy)               : Add/remove/update DNS record
- [ec2instance.py](https://github.com/vettom/Aws-Boto3#ec2instancepy)             : Manage Ec2 instance stop/start
- [elbctl.py](https://github.com/vettom/Aws-Boto3#elbctlpy)             : Mange Classig ELB 

# ![alt text](https://vettom.github.io/images/dv-tec-logo-round2cm.png "Denny Vettom  Tech Logo") Script details 

### dnsupdate.py
  Script can accept list of aliases or a list provided in a file. Zone ID is required, destzoneid required if destination alias in different DNS zone

``` 
usage: dnsctl.py [-h] (-s SRC_URL [SRC_URL ...] | -f SRC_FILE)
                 [-d DESTINATION] [-z ZONEID] [--destzoneid DESTZONEID]
                 [--health_check {True,False}]
                 {add,update,delete}

Manage routine DNS tasks.

positional arguments:
  {add,update,delete}   Choose task toperform

optional arguments:
  -h, --help            show this help message and exit
  -s SRC_URL [SRC_URL ...], --src_url SRC_URL [SRC_URL ...]
                        Alias/Domain name to be created separated by space
  -f SRC_FILE, --src_file SRC_FILE
                        File containing Alias list, one per line
  -d DESTINATION, --destination DESTINATION
                        Destination CNAME or IP
  -z ZONEID, --zoneid ZONEID
                        Zone ID, defaults to adobecqms ID
  --destzoneid DESTZONEID
                        Destination Zone ID for ELB only or if different
                        zoneid
  --health_check {True,False}
                        Evaluate health check, Default=False

Script to manage DNS record in adobecqms.net by default or provide -z zoneid
to create in another zone.
```

- Creating multiple alias record pointing to xyz.vettom.co.uk. Accept at command line or from file.

``` 
./dnsupdate.py add -s 123.vettom.co.uk abc.vettom.co.uk -d zyz.vettom.co.uk  
./dnsupdate.py add -f dns.txt -d zyz.vettom.co.uk -z ABCD
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

- List all ELB in a VPC in region eu-west-1 using profile dev

```
elbctl.py list --vpc vpc-9c8b9dsd -r eu-west-1 -p dev

```

- Status of elb
```
elbctl.py status --elb vettom

```

- Attach/Detach multiple servers from multiple elb in one command
```
elbctl.py attah/detach  --elb vettomelb1 vettom-elb2 -i i-07d9ff1c2d74269c4 i-0de28ee8dfd3ec57b

```

### ec2instance.py
Start/stop aws instance, list all instances and status of instance.

```
ec2instance.py -h
usage: ec2instance.py [-h] [--profile PROFILE] [--region REGION]
                      [--instance INSTANCE]
                      action

Perform common instance tasks

positional arguments:
  action               Instance action to be performed
                       list/start/stop/restart/status

optional arguments:
  -h, --help           show this help message and exit
  --profile PROFILE    If no profile provided, assumes default
  --region REGION      Default is eu-west-1, or provide as argument
  --instance INSTANCE  Name of Aws instance
```
