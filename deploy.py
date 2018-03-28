#!/usr/bin/env python3
# Author: Dael Saint-Surin
# Date: 03.25.2018
# File Name: deploy.py
# Purpose: To do a no downtime deployment of aws instances in 3 AZ.

import boto3
import sys
import os

def script_usage():
    '''This function will throw an Exception if there is no Authentication or no AvailabilityZone.'''
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

def get_image_id():
    return sys.argv[1], sys.argv[2]

def display_error(error):
    '''This function will be used to display an error.'''
    print('*' * 10)
    print(error)
    print('Please make the necessary correction and try again!')
    print('We are terminating the program!')
    print('*' * 10)
    exit()

def session_initialization():
    session = boto3.Session()
    if session.region_name == None:
        error = 'No AWS region was found in your .aws/config file'
        display_error(error)
    elif session.get_credentials() == None:
        error = 'We are unable to locate credentials on this machine!'
        display_error(error)
    else:
        ec2 = boto3.resource('ec2')
        client = boto3.client('ec2')
        return ec2, client

def validate_image_id(image_id, ec2):
    image = ec2.Image(image_id)
    try:
        image.state
    except:
        print('{} Image was not found'.format(image_id))
        exit()

def get_instance_attributes(image_id, client):
    'This will get the instance use by the image if any'
    desc_image = client.describe_instances(
        Filters=[
            {
                'Name' : 'image-id',
                'Values': [ image_id]
            }
        ]
    )
    try:
        instances_values = len(desc_image['Reservations'])
        if instances_values == 0:
            raise
        all_instance = []
        all_sec_group = []
        for i in range(instances_values):
            all_instance.append(desc_image['Reservations'][i]['Instances'][0]['InstanceId'])
            key_name = desc_image['Reservations'][i]['Instances'][0]['KeyName']
            av_zone = desc_image['Reservations'][i]['Instances'][0]['Placement']['AvailabilityZone']
            instance_type = desc_image['Reservations'][i]['Instances'][0]['InstanceType']
            sec_group = desc_image['Reservations'][i]['Instances'][0]['SecurityGroups']

            for j in range(len(sec_group)):
                all_sec_group.append(sec_group[j]['GroupName'])

        return all_instance, key_name, av_zone, instance_type, all_sec_group

    except:
        exit('{} is not in used by any instance'.format(image_id))

def start_instance(instance_id, client):
    client.start_instaces(InstanceIds = [ instance_id ])
    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds = [ instance_id ])
    return waiter.name

def stop_instance(instance_id, client):
    try:
        client.stop_instances(InstanceIds = instance_id )
        waiter = client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds = [ instance_id ])
        # if waiter.name == ''
    except ClientError as err:
        print(err)

def launch_new_instance(image_id, av_zone, instance_type, sec_groups, key_name, ec2, client):

    print('The script is running...')
    print('Instance from Image-id {} will be created'.format(image_id))
    l_instance = ec2.create_instances(
        ImageId = image_id,
        Placement = {
            'AvailabilityZone': av_zone
        },
        InstanceType = instance_type,
        SecurityGroups = sec_groups,
        KeyName = key_name,
        MaxCount = 1,
        MinCount = 1
    )

    waiter_launch = client.get_waiter('instance_exists')
    waiter_launch.wait( InstanceIds = [ l_instance[0].id ] )

    waiter_start = client.get_waiter('instance_status_ok')
    waiter_start.wait(InstanceIds = [ l_instance[0].id ] )

    waiter_system = client.get_waiter('system_status_ok')
    waiter_system.wait(InstanceIds = [ l_instance[0].id ] )

    # return l_instance[0].id, waiter_launch.name, waiter_start.name, waiter_system.name
    if waiter_system.name == 'SystemStatusOk':
        print('\nInstance: {} with image-id {} created and started successfully'.format(l_instance[0].id, image_id))
        print('Now stopping the old instance')
    else:
        print('\nThere was a problem during the lauch of the instance.')
        print('Program aborted')
        exit()

def deployment(image_1, image_2):
    ec2, client = session_initialization()
    validate_image_id(image_1, ec2)
    validate_image_id(image_2, ec2)
    instance_ids, key_name, av_zone, instance_type, all_sec_group = get_instance_attributes(image_1, client)
    av_zone = av_zone[:-1]
    for i in 'abc':
        av_zone = av_zone + i
        launch_new_instance(image_2, av_zone, instance_type, all_sec_group, key_name, ec2, client)
    for i in 'abc':
        av_zone = av_zone + i
        stop_instance(instance_ids, client)

def main():
    os.system('clear')
    script_usage()
    old_image_id, new_image_id = get_image_id()
    deployment(old_image_id, new_image_id)

if __name__ == '__main__':
    main()
