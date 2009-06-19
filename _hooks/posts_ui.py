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

import os
import time
import datetime
import tempfile
import textwrap
import readline
import urllib
import hashlib


def setup_posts_ui():

    def get_editor():
        editor = os.environ.get('GROWL_EDITOR')
        if not editor:
            editor = os.environ.get('EDITOR')
        if not editor:
            editor = 'vi'
        return editor

    def launch_editor(content = ''):
        fn = None
        try:
            fid, fn = tempfile.mkstemp('.post', 'growl_', None, True)
            f = open(fn, 'w')
            f.write(content)
            f.close()

            mod_time_start = os.stat(fn).st_mtime
            rcode = subprocess.call([get_editor(), fn])
            mod_time_end = os.stat(fn).st_mtime

            hash_org = hashlib.sha256(content).digest()
            f = open(fn, 'r')
            content = f.read()
            f.close()
            hash_new = hashlib.sha256(content).digest()

            if (rcode != 0 or
                    mod_time_end == mod_time_start or
                    hash_org == hash_new):
                return None

            # only delete temp file if anything went ok
            return content
        finally:
            if fn:
                os.unlink(fn)

    def raw_input_default(prompt, value = None):
        if value:
            readline.set_startup_hook(lambda: readline.insert_text(value))
        try:
            return raw_input(prompt)
        finally:
            if value:
                readline.set_startup_hook(None)

    def mangle_url(url):
        ou = url
        url = url.lower()
        url = ''.join(c for c in url if c not in mangle_url.SP)
        url = url.replace('&', ' and ')
        url = url.replace('.', ' dot ')
        url = url.strip()
        url = url.replace(' ', '_')
        return urllib.quote(url)
    mangle_url.SP = '`~!@#$%^*()+={}[]|\\;:\'",<>/?'

    def create_new_post(self):
        TEMPLATE = textwrap.dedent("""
        ---
        layout: post
        title: ???
        categories: ???
        ---
        """).strip()
        try:
            content = launch_editor(TEMPLATE)
            if content:
                # load yaml header
                mo = Template.RE_YAML.match(content)
                if mo and mo.groupdict().get('yaml'):
                    meta = yaml.load(mo.groupdict().get('yaml'))
                    title = meta.get('title')

                if title:
                    title = mangle_url(title)

                    tnow = datetime.datetime.now().timetuple()
                    filename = time.strftime('%Y-%m-%d-', tnow)
                    filename += title

                    try:
                        filename = raw_input_default('filename: ', filename)
                        filename = os.path.join(self.POST_DIR, filename)
                        f = open(filename, 'w')
                        f.write(content)
                        f.close()
                        print 'created post: %s' % filename
                    except KeyboardInterrupt:
                        # save backup to temp file
                        print '\nabort...'
                        fid, fn = tempfile.mkstemp('.post', 'growl_',
                                                   None, True)
                        f = open(fn, 'w')
                        f.write(content)
                        f.close()
                else:
                    print 'abort... (no title)'
            else:
                print 'abort...'
        except Exception, e:
            print 'can\'t create new post: %s' % e
            raise

    @wrap(Site.setupOptions)
    def setupOptions(forig, self, parser):
        forig(self, parser)
        parser.add_option('-n', '--newpost',
                          action = 'store_true', dest = 'new_post',
                          help = 'create new post')

    @wrap(Site.run)
    def site_run(forig, self):
        """ write all posts to the deploy directory.
        """
        if self.options.new_post:
            create_new_post(self)
        else:
            forig(self)

setup_posts_ui()
