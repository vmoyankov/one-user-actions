#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import user_action

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("0.0.0.0", 8001),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

def reset_password(auth, vid, password):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'reset_password', [password])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def update_network_config(auth, vid):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'update_network_config', [])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def clear_firewall(auth, vid):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'clear_firewall', [])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

def test(auth, vid):
    user_action.AUTH = auth
    res = user_action.remote_action(vid, 'guest_exec.py', [
        'sh', '-c', "'hostname; set; echo SUCCESS'"
        ])
    return (res[0] == 0, res[2] if res[0] else res[1], res[0])

server.register_function(reset_password, 'one.user_action.reset_password')
server.register_function(update_network_config, 'one.user_action.update_network_config')
server.register_function(clear_firewall, 'one.user_action.clear_firewall')
server.register_function(test, 'one.user_action.test')

server.serve_forever()
