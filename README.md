README.md

Requirements:
python3
pip
awscli
boto3


This script deploy.py requires python3, awscli and boto3 installed on the local system where will it be running. Additionally, the AWS command aws-cli must be installed and configured on that system, with the region from where the instances are installed. Credentials should be also set, other wise the script will fail.
Below is the configuration as it is on my system:

/Users/daelss45/.aws/config
/Users/daelss45/.aws/credentials

-rw-------  1 daelss45  staff   98 Mar 24 18:49 config
-rw-------  1 daelss45  staff  236 Mar 24 18:49 credentials

The script will take exactly 2 arguments, otherwise an error will be thrown and the script will executing.

To run the script, you may just run that command below, download the script to your machine, then issue that command:

python3 /path/to/deploy.py old-image-id new-image-id or Just give it write permission  (chmod 544 ./deploy.py, I assume you are in the same directory of the script) and run the command below from your Linux or Mac terminal:

./deploy.py old-image-id new-image-id.

The script will first try to run the new image, and once it is complete, it will stop the old image. If the new-image fail, the script will stop, and the old one will be kept in place.

If any of those two images (old-image-id or new-image-id) cannot be found on the aws system, the script will throw and error and stop.

I made several tests, and they were fine. There is still room to make improvements but I do not want to wait, we surely can discuss further.
