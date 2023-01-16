#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from xmlrpc.client import ServerProxy

URL = 'http://localhost:2634/RPC2'
AUTH = 'XXXX:XXXX'

server = ServerProxy(URL)
res = server.one.user_action.test(AUTH, int(sys.argv[1]), sys.argv[2])
print(res[0], res[2])
print(res[1])
