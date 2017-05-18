#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xml.etree.cElementTree as ET
import xmlrpclib
import subprocess
import os

ACTION_DIR = '/var/tmp/one/user_action'
URI = 'http://localhost:2633/RPC2'
AUTH = 'XXXX:XXXX'
SSH_USER = 'oneadmin'


def get_vm_info(id):

    import httplib

    class TimeoutTransport(xmlrpclib.Transport):
        timeout = 10.0
        def set_timeout(self, timeout):
            self.timeout = timeout
        def make_connection(self, host):
            h = httplib.HTTPConnection(host, timeout=self.timeout)
            return h

    t = TimeoutTransport()
    t.set_timeout(2.0)

    server = xmlrpclib.ServerProxy(URI, transport=t)
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
        host = vm.find("./HISTORY_RECORDS/HISTORY[ETIME='0']/HOSTNAME").text
    except AttributeError:
        return None
    return host

def get_vm_domain(vm):
    return vm.find('./DEPLOY_ID').text


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
        print res[1],
        print >>sys.stderr, res[2],
        sys.exit(res[0])
    else:
        print "Usage %s <VM_ID> <action> [args ...]" % sys.argv[0]
        sys.exit(os.EX_USAGE)


if __name__ == '__main__':
    main()
