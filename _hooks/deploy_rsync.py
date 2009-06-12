# vim:syntax=python:sw=4:ts=4:expandtab
#
# Copyright (C) 2009 Rico Schiekel (fire at downgra dot de)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

import subprocess

REMOTE_PATH = 'user@host:/path/'

@wrap(Site.setupOptions)
def setupOptions(forig, self, parser):
    forig(self, parser)
    parser.set_defaults(deploy = False)
    parser.add_option('--deploy',
                      action = 'store_true', dest = 'deploy',
                      help = 'deploy site')


@wrap(Site.run)
def run_rsync(forig, self):
    # first run 'default' actions and maybe other run hooks
    forig(self)

    if self.options.deploy:

        cmd = 'rsync -ahz --delete %s/* %s\n' % (self.DEPLOY_DIR, REMOTE_PATH)
        sys.stderr.write('deploy to >>> %s\n' % REMOTE_PATH)
        ret = subprocess.call(cmd, shell=True)
        if ret == 0:
            sys.stderr.write('<<< finished\n')
        else:
            sys.stderr.write('<<< failed! (return code: %d)\n' % ret)
