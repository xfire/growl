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
import sha

class Post(Page):
    """ a post template mapping a single post from the _posts/
        directory.
    """

    def __init__(self, filename, layout, context):
        super(Post, self).__init__(filename, layout, context)

        base = os.path.basename(filename)
        ext = os.path.splitext(base)

        self.year, self.month, self.day, self.slug = ext[0].split('-', 3)

        self.context.post = self

        cats = ','.join((self.context.get('category', ''),
                         self.context.get('categories', '')))
        if 'category' in self.context:
            del self.context['category']
        if 'categories' in self.context:
            del self.context['categories']
        self.categories = [c.strip() for c in cats.split(',') if c]

    @property
    def date(self):
        return datetime.datetime(int(self.year),
                                 int(self.month),
                                 int(self.day))

    @property
    def url(self):
        return os.path.join(self.year, self.month, self.day, self.slug)

    @property
    def path(self):
        return os.path.join(self.url, 'index' + self.POST_FILE_EXT)

    @property
    def content(self):
        return self.render()

    @property
    def publish(self):
        return self.context.get('publish', True)

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    @staticmethod
    def setup(clazz):
        clazz.POST_DIR = os.path.join(clazz.BASE_DIR, '_posts')

        def read_posts(self):
            self.posts = []
            if os.path.isdir(self.POST_DIR):
                self.posts = [Post(os.path.join(self.POST_DIR, f),
                                   self.layouts,
                                   self.context)
                                  for f in self.ignoreFilter(os.listdir(
                                                                self.POST_DIR))]
                self.context.site.posts = sorted(p for p in self.posts
                                                    if p.publish)
                self.context.site.unpublished_posts = sorted(p for p in self.posts
                                                                if not p.publish)

        def calc_categories(self):
            self.categories = AttrDict()
            for post in self.posts:
                if post.publish:
                    for cat in post.categories:
                        self.categories.setdefault(cat, []).append(post)
                    if not post.categories:
                        self.categories.setdefault(None, []).append(post)
            self.context.site.categories = self.categories

        def write_posts(self):
            for p in self.posts:
                p.write()

# ----------------------------------------------------------------------------------------

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

                hash_org = sha.new(content).digest()
                f = open(fn, 'r')
                content = f.read()
                f.close()
                hash_new = sha.new(content).digest()

                if rcode != 0 or mod_time_end == mod_time_start or hash_org == hash_new:
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

                        filename = time.strftime('%Y-%m-%d-', datetime.datetime.now().timetuple())
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
                            fid, fn = tempfile.mkstemp('.post', 'growl_', None, True)
                            f = open(fn, 'w')
                            f.write(content)
                            f.close()
                else:
                    print 'abort...'
            except Exception, e:
                print 'can\'t create new post: %s' % e

        @wrap(clazz.setupOptions)
        def setupOptions(forig, self, parser):
            forig(self, parser)
            parser.add_option('-n', '--newpost',
                              action = 'store_true', dest = 'new_post',
                              help = 'create new post')

# ----------------------------------------------------------------------------------------


        @wrap(clazz.prepare)
        def site_prepare(forig, self):
            """ read all posts and calculate the categories.
            """
            forig(self)
            read_posts(self)
            calc_categories(self)
        
        @wrap(clazz.run)
        def site_run(forig, self):
            """ write all posts to the deploy directory.
            """
            if self.options.new_post:
                create_new_post(self)
            else:
                write_posts(self)
                forig(self)

Post.setup(Site) # whooha!

