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
import json
import subprocess
import time
import base64

def get_output(domain, pid, timeout=5):
    ga_cmd = {
            'execute': 'guest-exec-status',
            'arguments': {
                'pid': pid}}

    start_time = time.time()
    ready = False
    while not ready:
        result_str = subprocess.check_output(
                ['virsh', '--connect', 'qemu:///system',
                    'qemu-agent-command', domain, json.dumps(ga_cmd)]
                )
        res = json.loads(result_str)
        ready = res['return']['exited']
        if not ready:
            if (time.time() - start_time > timeout):
                return None
            time.sleep(0.5)
    return res

def guest_exec(domain, cmd, argv, wait=True):
    ga_cmd = {
            'execute': 'guest-exec',
            'arguments': {
                "path": cmd,
                "arg": argv,
                "capture-output": True
                }
            }
    try:
        result_str = subprocess.check_output(
                ['virsh', '--connect', 'qemu:///system',
                    'qemu-agent-command', domain, json.dumps(ga_cmd)]
                )
    except subprocess.CalledProcessError as e:
        return(e.returncode, e.output, '')
    res = json.loads(result_str)
    pid = res['return']['pid']

    out = None
    if wait:
        res = get_output(domain, pid)
        if res is None:
            return (127, '', 'Timeout executing guest agent command')
        r = res['return']
        exitcode = r.get('exitcode')
        out = base64.b64decode(r.get('out-data', b''))
        err = base64.b64decode(r.get('err-data', b''))
        return (exitcode, out, err)
    return (0, '', '')

def main():
    import os
    if len(sys.argv) > 2:
        out = guest_exec(sys.argv[1], sys.argv[2], sys.argv[3:], wait=True)
        sys.stdout.buffer.write(out[1])
        sys.stderr.buffer.write(out[2])
        sys.exit(out[0])
    else:
        print("Usage %s <domain> <cmd> [<args>, ...]" % sys.argv[0],
                file=sys.stderr)
        sys.exit(os.EX_USAGE)

if __name__ == '__main__':
    main()
