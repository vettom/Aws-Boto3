# Python - Aws Boto3 Scripts
**Collection of Python3 scripts to manage AWS instance with help of Boto3. Scripts are written in self help mode.**
> scriptname -h for help
> All scripts expect AWS cli to be configured and at least profile called default

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

Example of creating alias 123.vettom.co.uk pointing to xyz.vettom.co.uk
` ./dnsupdate.py alias -s 123.vettom.co.uk -d zyz.vettom.co.uk -z ABCD `