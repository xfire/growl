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
import datetime


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
                self.context.site.unpublished_posts = sorted(p for
                                                             p in self.posts
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
            write_posts(self)
            forig(self)

Post.setup(Site) # whooha!
