#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ForkingMixIn


import user_action

class ForkingServer(ForkingMixIn, SimpleXMLRPCServer):
    pass

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = ForkingServer(("0.0.0.0", 2634),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

def reset_password(auth, vid, password):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'reset_password', [password])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def reset_network_config(auth, vid):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'reset_network_config', [])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def clear_firewall(auth, vid):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'clear_firewall', [])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def add_ip_alias(auth, vid, if_idx, address):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'network_ip_alias',
                ['add', str(if_idx), address])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def del_ip_alias(auth, vid, if_idx, address):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'network_ip_alias',
            ['delete', str(if_idx), address])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def test(auth, vid, msg):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'test', [msg])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def u_exec(auth, vid, cmd):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'guest_exec', [cmd])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

server.register_function(reset_password, 'one.user_action.reset_password')
server.register_function(reset_network_config, 'one.user_action.reset_network_config')
server.register_function(clear_firewall, 'one.user_action.clear_firewall')
server.register_function(add_ip_alias, 'one.user_action.add_ip_alias')
server.register_function(del_ip_alias, 'one.user_action.del_ip_alias')
server.register_function(test, 'one.user_action.test')
server.register_function(u_exec, 'one.user_action.execute')

if '-d' in sys.argv:
    pid = os.fork()
    if pid:
        print "server running in background. pid: %d" % pid
        sys.exit(0)
server.serve_forever()
