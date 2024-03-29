#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################################################
# Copyright 2017 Telera www.telera.eu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

import sys
import xml.etree.cElementTree as ET
import subprocess
import os

from xmlrpc.client import ServerProxy
from xmlrpc.client import Transport

ACTION_DIR = '/var/tmp/one/user_action'
URI = 'http://localhost:2633/RPC2'
AUTH = 'XXXX:XXXX'
SSH_USER = 'oneadmin'

server = None

def connect_to_server(URI):
    import http.client

    class TimeoutTransport(Transport):
        timeout = 10.0
        def set_timeout(self, timeout):
            self.timeout = timeout
        def make_connection(self, host):
            h = http.client.HTTPConnection(host, timeout=self.timeout)
            return h

    t = TimeoutTransport()
    t.set_timeout(2.0)
    server = ServerProxy(URI, transport=t)
    return server

def get_vm_info(id):
    global server

    if server is None:
        server = connect_to_server(URI)

    ok, res, code = server.one.vmpool.info(
            AUTH,
            -2,  # all resources
            id, # range start
            id, # range end
            -2  # state ANY
            )
    if not ok:
        return None
    root = ET.fromstring(res)
    vm = root.find('VM')
    return vm

def get_vm_host(vm):
    try:
        host = vm.find("./HISTORY_RECORDS/HISTORY/HOSTNAME").text
    except AttributeError:
        return None
    return host

def get_vm_domain(vm):
    return vm.find('./DEPLOY_ID').text

def get_vm_id(vm):
    return int(vm.find('./ID').text)

def get_vm_context(vm):
    try:
        ctx = vm.find('./TEMPLATE/CONTEXT')
    except AttributeError:
        return None
    return ctx

def set_vm_context(vm,ctx):
    global server

    vmid = get_vm_id(vm)
    xml = ET.tostring(ctx)

    if server is None:
        server = connect_to_server(URI)

    ok, res, code = server.one.vm.updateconf(
            AUTH,
            vmid,
            xml
            )
    if not ok:
        return None
    return res

def execute_remote(host, cmd):

    cmd_list = ['ssh', '-oBatchMode=yes', '-l', SSH_USER, host ] + cmd
    p = subprocess.Popen(cmd_list,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    exit_code = p.returncode

    return (exit_code, out, err)

def remote_action(vid, action, params):
    if '/' in action:
        raise ValueError('Invalid action format')
    vm = get_vm_info(vid)
    if not vm:
        return(255, '', 'Can not get VM. ID is incorrect, no permissions, or no access to OpenNebula')
    host = get_vm_host(vm)
    if not host:
        return(254, '', 'VM is not depolyed')
    vm_domain = get_vm_domain(vm)
    cmd_list = [ ACTION_DIR + '/' + action, vm_domain ] + params
    return execute_remote(host, cmd_list)


def main():
    if len(sys.argv) > 2:
        res = remote_action(int(sys.argv[1]), sys.argv[2], sys.argv[3:])
        sys.stdout.buffer.write(res[1])
        sys.stderr.buffer.write(res[2])
        sys.exit(res[0])
    else:
        print("Usage %s <VM_ID> <action> [args ...]" % sys.argv[0])
        sys.exit(os.EX_USAGE)


if __name__ == '__main__':
    main()
