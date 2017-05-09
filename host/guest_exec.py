#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import subprocess
import time

def get_output(domain, pid, timeout=5):
    ga_cmd = {
            'execute': 'guest-exec-status',
            'arguments': {
                'pid': pid}}

    start_time = time.time()
    ready = False
    while not ready:
        result_str = subprocess.check_output(
                ['virsh', 'qemu-agent-command', domain, json.dumps(ga_cmd)]
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
    result_str = subprocess.check_output(
            ['virsh', 'qemu-agent-command', domain, json.dumps(ga_cmd)]
            )
    res = json.loads(result_str)
    pid = res['return']['pid']

    out = None
    if wait:
        res = get_output(domain, pid)
        if res is None:
            return (127, '', 'Timeout executing guest agent command')
        r = res['return']
        exitcode = r.get('exitcode')
        out = r.get('out-data','').decode('base64')
        err = r.get('err-data','').decode('base64')
        return (exitcode, out, err)
    return (0, '', '')

def main():
    import os
    if len(sys.argv) > 2:
        out = guest_exec(sys.argv[1], sys.argv[2], sys.argv[3:], wait=True)
        print out[1],
        print >> sys.stderr, out[2],
        sys.exit(out[0])
    else:
        print >>sys.stderr, "Usage %s <domain> <cmd> [<args>, ...]" % sys.argv[0]
        sys.exit(os.EX_USAGE)

if __name__ == '__main__':
    main()
