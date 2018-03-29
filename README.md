# README.md
### 
```sh
deploy.py
```
This is a simple script that use the AWS boto3 module to query teh AWS api. For the script to work, a few packages must be installed on the local computer where the script will be running to query the AWS Platform. The script will query 3 images on 3 differents availability zone, and will try to replace those old images with 3 new images, buy building 3 new instances one in AZ. When the creation of these new instances have been successfully completed and running, the scrip will shutdown the 3 old instances. Simply put, the script will attempt to do a deployment with 0 downtime.

### Requirements:
- python3
- boto3
- os
- sys
- awscli
- valid iam account
- aws must be configure

### Below is a test that shows data as the script is running.
The script will take two arguments, they must be two amazone machine image, failing to do so will throw an error and the script will stop running. Below is the output, with no argument:
##### Output from MacOS High Sierra

```sh
daelss45$ ./deploy.py ami-4543be3d ami-79873901 ami-ea950192
**********
Script incorrect USAGE
USAGE: ./deploy.py OLD_AMI_ID NEW_AMI_ID
OLD_AMI_ID is an old image-id
NEW_AMI_ID is the new image-id
**********
```

```
##### output from Ubuntu
```sh
daelss45@miaflub001:~$ cat /etc/lsb-release 
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=16.10
DISTRIB_CODENAME=yakkety
DISTRIB_DESCRIPTION="Ubuntu 16.10"
daelss45@miaflub001:~$ python deploy.py 
**********
Script incorrect USAGE
USAGE: deploy.py OLD_AMI_ID NEW_AMI_ID
OLD_AMI_ID is an old image-id
NEW_AMI_ID is the new image-id
**********
daelss45@miaflub001:~$ 
```

### Other requirements. 
aws package must be locally installed on the local machine. There are a few tutorials on AWS that shows how to do it. I made a few test on 3 different platform (macbook pro 10.13, ubunut 16.10 and Centos 7.4x), but similar, and they each were susccessfully.

### what if no aws config or credentials.
An error similar to below will be thrown
```bash
daelss45@miaflub001:~$ python ./deploy.py  ami-79873901 ami-4543be3d 
**********
We are unable to locate credentials on this machine!
Please make the necessary correction and try again!
We are terminating the program!
**********
daelss45@miaflub001:~$ 
```

### When all requirements were met, we should see a screen as below:
```bash
daelss45$ ./deploy.py  ami-79873901 ami-4543be3d 
The script is running...
Instance from Image-id ami-4543be3d will be created

Instance: i-0eb343922bb7128dc with image-id ami-4543be3d created and started successfully
The script is running...
Instance from Image-id ami-4543be3d will be created

Instance: i-03be4e6c70dea10c8 with image-id ami-4543be3d created and started successfully
The script is running...
Instance from Image-id ami-4543be3d will be created

Instance: i-0d69e9d09e7675b6f with image-id ami-4543be3d created and started successfully
Instance has been stopped successfully
Instance has been stopped successfully
Instance has been stopped successfully
daelss45$
```
