#!/usr/bin/python3

import json
import subprocess
import argparse

class MyInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.populate()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print (json.dumps(self.inventory));

    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    def populate(self):
        '''Populate inventory with given instances'''
        cmd = ["yc", "compute", "instance", "list", "--format", "json"]
        output = subprocess.run(cmd, stdout=subprocess.PIPE)
        yc_obj = json.loads(output.stdout)
        hostname = []
        ip_app = []
        ip_db = []
        for instance in yc_obj:
            hostname.append(instance.get('name'))
            if "app" in instance.get('name'):
                ip_app.append(instance
                    .get('network_interfaces', [{}])[0]
                    .get('primary_v4_address', {})
                    .get('one_to_one_nat', {})
                    .get('address'))
            elif "db" in instance.get('name'):
                ip_db.append(instance
                    .get('network_interfaces', [{}])[0]
                    .get('primary_v4_address', {})
                    .get('one_to_one_nat', {})
                    .get('address'))

        return {
            'app': {
                'hosts': ip_app,
            },
            'db': {
                'hosts': ip_db,
            },
            '_meta': {
                'hostvars': {
                }
            }
        }

    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}



# Get the inventory.
MyInventory()
