#!/usr/bin/env python3
# Author: Dael Saint-Surin
# Date: 03.25.2018
# File Name: deploy.py
# Purpose: To do a no downtime deployment of aws instances in 3 AZ.

import boto3
import sys
import os
import time

def script_usage():
    '''
    This function will throw an Exception if there is no Authentication or no AvailabilityZone.
    '''
    if len(sys.argv) != 3:
        print('\n')
        print('*' * 10)
        print ('Script incorrect USAGE')
        print ('USAGE: {0} OLD_AMI_ID NEW_AMI_ID'.format(sys.argv[0]))
        print ('OLD_AMI_ID is an old image-id')
        print ('NEW_AMI_ID is the new image-id')
        print('*' * 10)
        print('\n')
        exit()
    else:
        old_image_id = sys.argv[1]
        new_image_id = sys.argv[2]
        return old_image_id, new_image_id



def display_error(error):
    '''
    This function will be used to display an error.
    '''
    print('*' * 10)
    print(error)
    print('Please make the necessary correction and try again!')
    print('We are terminating the program!')
    print('*' * 10)
    exit()

def session_initialization():
    session = boto3.Session()
    if session.region_name == None:
        error = 'Region is missing.'
        display_error(error)
    elif session.get_credentials() == None:
        error = 'We are unable to locate credentials on this machine!'
        display_error(error)
    else:
        ec2 = session.resource('ec2')
        return ec2, session


def get_old_instance_id(old_image_id, new_image_id):
    '''
    This function will validate both the old-image-id and the new-image-id exist on AWS
    it will trow an  error and stop the script if any of the images is not found.
    it will return 3 values:
    old_instance_id - the old object instance id
    old_image_id - old image id
    new_image_id - new image id
    '''
    ec2, session = session_initialization()
    all_instance_id = []
    all_image_id = {}

    for instance in ec2.instances.all():
        all_instance_id.append(instance)
        all_image_id[instance] = instance.image_id

    total_instance = len(all_instance_id)
    count_instance = 0
    old_instance_id = None
    for instance_id in all_instance_id:
        count_instance = count_instance + 1

        if old_image_id != instance.image_id:
            pass
        elif old_image_id == instance.image_id:
            old_instance_id = instance_id
            # print(old_image_id, instance_id)

            break
        if count_instance == total_instance and old_instance_id is None:
            print('OLD-Image {} was not found in that in region {}.'.format(old_image_id, session.region_name))
            print('The script is stopped, no further action will be taken!')
            exit()
    # print(all_image_id)
    if new_image_id not in all_image_id.values():
        print('New-Image {} was not found in that {}.'.format(new_image_id, session.region_name))
        print('The script is stopped, no further action will be taken!')
        exit()
    # old_instance_id is an object id
    old_instance_id = old_instance_id
    return old_instance_id, old_image_id, new_image_id

def stop_instances(instance_id):
    '''This can be used to stop an instance'''
    session = boto3.Session()
    client = session.client('ec2')
    client_object_id = client.stop_instances(InstanceIds=[ instance_id ])
    time.sleep(60)
    return client_object_id


def start_instances(instance_id):
    '''This will be used to stop an instance'''
    client = session.client('ec2')
    start_instance = client.start_instances(InstanceIds=[ instance_id ])


def get_instance_security_group(instance_id):
    '''This will be used to get the security group id of the old instance'''
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    security_group = []
    groups = instance.describe_attribute(Attribute='groupSet')
    for group in groups['Groups']:
        g = groups['Groups'][0]['GroupId']
        security_group.append(g)
    return security_group

def get_instance_type(instance_id):
    '''This function will be used to get the instancetype'''
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    instance = instance.describe_attribute(Attribute='instanceType')
    instance_type = instance['InstanceType']['Value']
    return instance_type

def get_instance_state(instance_id):
    session = boto3.Session()
    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    instance_state = instance.state['Name']
    return instance_state


def get_instance_key_name(instance_object):

    key_name = instance_object.key_name
    return key_name



def launch_new_instance(new_image_id, AZ, instanceType, security_group, key_name):
    '''
    This function takes 4 parameters, and create a new instance, and it returns the instance object id.
    new_image_id is the new Image-id
    AZ is the AvailabilityZone where the new instance will be launched
    instanceType: The type of the instance, (t2.micro, t2.nano, etc..)
    security_group: the Security Group inherited from the old instance
    key_name: the key_name inherited from the old instance.
    '''
    print('Create and Launch the new Instance Image-ID: {}'.format(new_image_id))
    print('This will be create on AvailabilityZone: {}'.format(AZ))
    session = boto3.Session()
    ec2 = session.resource('ec2')
    instance = ec2.create_instances(
        ImageId=new_image_id,
        Placement={
            'AvailabilityZone': AZ
        },
        SecurityGroupIds=security_group,
        InstanceType=instanceType,
        MaxCount=1,
        MinCount=1,
        KeyName=key_name
    )
    time.sleep(300)
    new_instance_object = instance[0]

    # print (new_instance_object)
    return instance[0]

def one_zone(id):
    # os.system('clear')
    old, new = script_usage()
    instance_object, old_image_id, new_image_id = get_old_instance_id(old, new)
    old_instance_id = instance_object.instance_id
    AZ = instance_object.placement['AvailabilityZone']
    AZ = AZ[:-1] + id
    instanceType = get_instance_type(old_instance_id)
    security_group = get_instance_security_group(old_instance_id)
    key_name = get_instance_key_name(instance_object)

    new_instance_object = launch_new_instance(new_image_id, AZ, instanceType, security_group, key_name)

    print('The instance was launched successfully on Zone: {}'.format(AZ))

    new_instance_id = new_instance_object.instance_id
    state = get_instance_state(new_instance_id)

    if state == 'running':
        try:
            status_old_instance = stop_instances(old_instance_id)
            raise Exception(status_old_instance)
        except Exception as state_error:
            print('Instance ID {} has been stopped'.format(old_instance_id))


def deployment_all_AZ():
    zone_id = list('abc')
    for id in zone_id:
        one_zone(id)

def main():
    os.system('clear')
    script_usage()
    deployment_all_AZ()

if __name__ == '__main__':
    main()
