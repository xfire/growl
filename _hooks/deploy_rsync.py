#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import subprocess

REMOTE_PATH = 'user@host:/path/'

@wrap(Site.deploy)
def deploy_rsync(self):
    cmd = 'rsync -ahz --delete %s/* %s\n' % (self.DEPLOY_DIR, REMOTE_PATH)
    sys.stderr.write('deploy to >>> %s\n' % REMOTE_PATH)
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        sys.stderr.write('<<< finished\n')
    else:
        sys.stderr.write('<<< failed! (return code: %d)\n' % ret)
    return deploy_rsync.super(self)

