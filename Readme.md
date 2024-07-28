<a href="https://vettom.github.io/"><img src="https://vettom.github.io/img/vettom-banner.jpg" alt="vettom.github.io" ></a>

# Python 3.x - Aws Boto3 Scripts ![alt text]([[https://vettom.github.io/images/RobinR100px.png](https://avatars.githubusercontent.com/u/20859413?v=4)](https://avatars.githubusercontent.com/u/20859413?v=4) "Denny Vettom Logo")

# Development Principle
<img src="https://vettom.github.io/img/dvethos.jpg" >

## Getting Started
- [X] All scripts are written in Python 3.x and requires Boto3
- [X] Authentication is via credentials and profile you have configured in $HOME/.aws (Same files as AWS CLI )
- [X] Unless specified as 'Generic', script rely on dvclass and a custom CMDB file for making decisions easy.
- [X] All scripts will have help available by running -h



# ![alt text](https://vettom.github.io/images/dv-tec-logo-round2cm.png "Denny Vettom  Tech Logo") Scripts (Requires Custom CMDB)
- [albctl.py](https://github.com/vettom/Aws-Boto3#albctlpy)             : Custom, list/status/detach/attach multiple ALB and instances.  
- [dnsctl.py](https://github.com/vettom/Aws-Boto3#dnsupdatepy)               : Add/remove/update DNS record
- [elbctl.py](https://github.com/vettom/Aws-Boto3#elbctlpy)             : Custom, mange Classig ELB 
- [dvsnaps.py](https://github.com/vettom/Aws-Boto3#dvsnapspy)             :  Cutom, manage Snapshot tasks. Requires my CMDB 

## Generic scripts ()
- [lb-whitelistcheck.py](https://github.com/vettom/Aws-Boto3#lb-whitelistcheckpy)       : Check if IP is whitelisted on ELB/ALB or print all SG rules attached to ALB/ELB
- [ec2instance.py](https://github.com/vettom/Aws-Boto3#ec2instancepy)       : Generic,  manage Ec2 instance stop/start
- [elbctlv1.py](https://github.com/vettom/Aws-Boto3#elbctlv1py)             : Generic mange Classic ELB

# ![alt text](https://vettom.github.io/images/dv-tec-logo-round2cm.png "Denny Vettom  Tech Logo") Script details 

### lb-whitelistcheck.py
    Accept ELB/ALB name as input along with profile and region (or Default and eu-west-1 used)
    - Print all rules attached to ELB/ALB
    - Check if specifies IP's are whitelisted or not, and if whitelisted Rule is displayed with SG name

```python
./lb-whitelistcheck.py
usage: lb-whitelistcheck.py [-h] {alb,elb,albcheck,elbcheck} ...

Print all SG rules or check if specified IP addresses are whitelisted for LB
or not.

optional arguments:
  -h, --help            show this help message and exit

Required arguments:
  {alb,elb,albcheck,elbcheck}
    alb                 Print all SecurityGroup Rules attached to ALB
    elb                 Print SecurityGroup all Rules attached to ALB
    albcheck            Check if provided IP/s are whitelisted on ALB and
                        prints rule and ServiceGroup name
    elbcheck            Check if IP/s are whitelisted on ELB and prints rule
                        and ServiceGroup name

```

### albctl.py (ElB v2)
  List/status : Can list/status of all ALB associated with Topoligy VPC.
  Attach/detach : Accepts multiple ALB, Instances. All instances must be in same region. Unless TG name specified all TG for ALB will be updated.

```python
  Required arguments:
  {list,status,attach,detach}
    list                Show list of all ALB configured for Topology
    status              Show status of all ALB configured for Topology. Use -e
                        or -t
    attach              Attach instance/s to ALB, apply to all TG unless
                        specified.
    detach              Detach instance/s to ALB, apply to all TG unless
                        specified.
  ```

### dnsctl.py
  Helps with creation of DNS record. Ideal scenario will be when many DNA names are pointing to single CNAME. 
 >Script can accept list of aliases or a list provided in a file. Zone ID is required, destzoneid required if destination alias in different DNS zone

```python
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
                        Zone ID, defaults to vettomcqms ID
  --destzoneid DESTZONEID
                        Destination Zone ID for ELB only or if different
                        zoneid
  --health_check {True,False}
                        Evaluate health check, Default=False

Script to manage DNS record in vettomcqms.net by default or provide -z zoneid
to create in another zone.
```

- Creating multiple alias record pointing to xyz.vettom.co.uk. Accept at command line or from file.

``` bash
./dnsupdate.py add -s 123.vettom.co.uk abc.vettom.co.uk -d zyz.vettom.co.uk  
./dnsupdate.py add -f dns.txt -d zyz.vettom.co.uk -z ABCD
```

### elbctl.py
  Manage classic loadbalancer. List ELB in a VPC, status of ELB's, attach/detach instances

  > Script can accept multiple ELB, and instances, but all must be in same vpc. If multiple instances provided for attach/detach same action performed on all ELB names provided.

```python
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

```bash
elbctl.py list --vpc vpc-9c8b9dsd -r eu-west-1 -p dev

```

- Status of elb
```bash
elbctl.py status --elb vettom

```

- Attach/Detach multiple servers from multiple elb in one command
```python
elbctl.py attah/detach  --elb vettomelb1 vettom-elb2 -i i-07d9ff1c2d74269c4 i-0de28ee8dfd3ec57b

```

### ec2instance.py
Start/stop aws instance, list all instances and status of instance.

```python
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


### dvsnaps.py
Create/List snapshots. Clone option to take snapshot and replace it on destination host. Copy option to take snapshot and mount it in parallel on destination host. Listvol to list all volumes.

```python
usage: dvsnaps.py [-h] {list,listvol,snap,clone,copy,rmvol} ...

Manage routine snapshot tasks.

optional arguments:
  -h, --help            show this help message and exit

Required arguments:
  {list,listvol,snap,clone,copy,rmvol}
    list                List snapshots in last 10days or date specified
    listvol             List volume and size of volumes
    snap                Create snapshot of volume provided as argument
    clone               Attach snap of Source disk to Dest by replacing
                        dest_device
    copy                Attach snapshot of Source to destination for parallel
                        mounting
    rmvol               Detach and remove unused volume

Script requires CMDB with hosts detail. Scripts uses CMDB to speed up decition

```

### elbctlv1.py
```python
usage: elbctlv1.py [-h] -a {list,status,attach,detach} [-p PROFILE]
                   [-r REGION] [--elb ELB [ELB ...]] [--vpc VPC [VPC ...]]
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

  
  
