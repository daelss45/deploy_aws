README.md

Requirements:
python3
pip
awscli
boto3


This scritp will required python3 and boto3 installed on the local system where
will be run. Additionally, the aws-cli must be installed and configured on that
system, with the region from where the instances are installed.
The user credentials should be also set, as the script will read the credentials
from that file as well, in my case, those two files are in:
/Users/daelss45/.aws/config
/Users/daelss45/.aws/credentials, with permission for both 400.
daelss45$ ll
total 16
-rw-------  1 daelss45  staff   98 Mar 24 18:49 config
-rw-------  1 daelss45  staff  236 Mar 24 18:49 credentials

The scrip will take exactly 2 arguments, an error will be trown and the script 
will be stopped its execution is this condition is not met.

To run the script, you may just run that command below
Download the script to your machine, then issue that command:

python3 /path/to/deploy.py old-image-id new-image-id

or you can just give it write permission and run the command below:
./deploy.py old-image-id new-image-id

After the script finish to run, the old-image-id instance will be stopped after
the new-image-id has been started and running successfully.

if any of those two images (old-image-id or new-image-id) cannot be found on
the aws system, the script will throw and error and stop.

I made several tests, and they were fine. There is still room to make improvements
but I do not want to wait, we surely can discuss further.
