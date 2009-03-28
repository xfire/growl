#!/usr/bin/env python
#
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

__author__ = 'Rico Schiekel <fire@downgra.de>'
__copyright__ = 'Copyright (C) 2009 Rico Schiekel'
__license__ = 'GPLv2'
__version__ = '0.1'


import os
import sys
import re
import shutil
import datetime
import collections
import itertools
import functools

import yaml


def renderTemplate(template, context):
    raise NotImplementedError('no template engine configured!')

try:
    import jinja2

    def renderTemplate(template, context):
        return jinja2.Template(template).render(context)

    def templateFilter(func):
        """ decorator to easily create jinja2 filters
        """
        jinja2.Template('').environment.filters[func.__name__] = func
except ImportError:
    pass


class AttrDict(dict):

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def copy(self):
        return AttrDict(super(AttrDict, self).copy())


class Config(object):

    @classmethod
    def updateconfig(cls, base, deploy):
        cls.transformers = {}
        cls.BASE_DIR = base
        cls.DEPLOY_DIR = deploy
        cls.LAYOUT_DIR = os.path.join(base, '_layout')
        cls.POST_DIR = os.path.join(base, '_posts')
        cls.HOOK_DIR = os.path.join(base, '_hooks')
        cls.LIB_DIR = os.path.join(base, '_libs')


class Template(Config):

    RE_YAML = re.compile(r'(^---\s*$(?P<yaml>.*?)^---\s*$)?(?P<content>.*)',
                         re.M | re.S)

    def __init__(self, filename, layouts, context):
        super(Template, self).__init__()
        self.filename = filename
        self.layouts = layouts
        self.context = context.copy()
        self.read_yaml()

    def read_yaml(self):
        self._content = file(self.filename, 'r').read()

        mo = self.RE_YAML.match(self._content)
        if mo and mo.groupdict().get('yaml'):
            self.context.update(yaml.load(mo.groupdict().get('yaml')))
            self._content = mo.groupdict().get('content')

    def transform(self):
        ext = os.path.splitext(self.filename)[-1][1:]
        t = self.transformers.get(ext, lambda x: x)
        return t(self._content)

    def render(self):
        ctx = self.context.copy()
        ctx.content = renderTemplate(self.transform(), ctx)
        layout = self.layouts.get(ctx.layout)
        if layout:
            return renderTemplate(layout.content, ctx)
        else:
            return ctx.content

    def layout(self):
        ctx = self.context.copy()
        ctx.content = self.render()
        layout = self.layouts.get(ctx.layout)
        if layout:
            layout = self.layouts.get(layout.layout)

        while layout != None:
            ctx.content = renderTemplate(layout.content, ctx)
            layout = self.layouts.get(layout.layout)

        return ctx.content

    def write(self, path, content):
        fname = os.path.join(self.DEPLOY_DIR, path)
        dirname = os.path.dirname(fname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        f = file(fname, 'w')
        f.write(content)
        f.close()

    def __getattr__(self, name):
        if not name in self.context:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                    (self.__class__.__name__, name))
        return self.context[name]


class Layout(Template):

    def __init__(self, filename, context):
        super(Layout, self).__init__(filename, {}, context)

        base = os.path.basename(filename)
        ext = os.path.splitext(base)
        self.name = ext[0]

    @property
    def layout(self):
        return self.context.get('layout')

    @property
    def content(self):
        return self.transform()


class Page(Template):

    def __init__(self, filename, layout, context):
        super(Page, self).__init__(filename, layout, context)

        self.context.page = self

    @property
    def url(self):
        return self.path.replace(os.path.sep, '/')

    @property
    def path(self):
        path = os.path.abspath(self.filename)[:-1]
        path = path.replace(os.path.abspath(self.BASE_DIR), '', 1)
        return path.lstrip(os.path.sep)

    @property
    def content(self):
        return self.render()

    def write(self):
        return super(Page, self).write(self.path, self.layout())


class Post(Page):

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
        return self.path

    @property
    def path(self):
        return os.path.join(self.year, self.month, self.day,
                            self.slug, 'index.xhtml')

    @property
    def content(self):
        return self.render()

    def __cmp__(self, other):
        return cmp(self.date, other.date)


class Site(Config):

    CONTEXT = AttrDict()

    def __init__(self):
        super(Site, self).__init__()

        if not self.LIB_DIR in sys.path and os.path.isdir(self.LIB_DIR):
            sys.path.append(self.LIB_DIR)

        self.layouts = {}
        self.posts = []

        self.hooks()

        self.context = Site.CONTEXT.copy()
        if not 'site' in self.context:
            self.context.site = AttrDict()

        self.context.site.now = datetime.datetime.now()

    def hooks(self):
        if os.path.isdir(self.HOOK_DIR):
            for f in sorted(os.listdir(self.HOOK_DIR)):
                if f.endswith('.py'):
                    execfile(os.path.join(self.HOOK_DIR, f), globals())

    def read(self):
        self.read_layouts()
        self.read_posts()
        self.calc_categories()

    def generate(self):
        self.write_posts()
        self.write_site_content()

    def deploy(self):
        pass

    def read_layouts(self):
        if os.path.isdir(self.LAYOUT_DIR):
            self.layouts = [Layout(os.path.join(self.LAYOUT_DIR, f),
                                   self.context)
                                for f in os.listdir(self.LAYOUT_DIR)
                                    if not f.startswith('__')]
            self.layouts = dict((l.name, l) for l in self.layouts)

    def read_posts(self):
        if os.path.isdir(self.POST_DIR):
            self.posts = [Post(os.path.join(self.POST_DIR, f),
                               self.layouts,
                               self.context)
                              for f in os.listdir(self.POST_DIR)
                                  if not f.startswith('__')]
            self.context.site.posts = sorted(self.posts)

    def calc_categories(self):
        self.categories = AttrDict()
        for post in self.posts:
            for cat in post.categories:
                self.categories.setdefault(cat, []).append(post)
        self.context.site.categories = self.categories

    def write_posts(self):
        for p in self.posts:
            p.write()

    IGNORE = ('_', '.')
    TRANSFORM = ('_', )

    def write_site_content(self):
        """ copy site content to deploy directory.

            ignoring all files and directories, if their filename
            begins with a token defined in IGNORE.

            files which end with an underscore are processed
            with the Page class and the underscrore is
            stripped from the output filename.
        """
        def ignore_filter(item):
            for ign in self.IGNORE:
                if item.startswith(ign):
                    return False
            return True

        ignore = functools.partial(itertools.ifilter, ignore_filter)

        def transformable(item):
            for trn in self.TRANSFORM:
                if item.endswith(trn):
                    return True
            return False

        for root, dirs, files in os.walk(self.BASE_DIR):
            base = root.replace(self.BASE_DIR, '')

            for d in ignore(dirs):
                    nd = os.path.join(self.DEPLOY_DIR, base, d)
                    if not os.path.isdir(nd):
                        os.makedirs(nd)
            dirs[:] = ignore(dirs)

            for f in ignore(files):
                if transformable(f):
                    Page(os.path.join(root, f),
                         self.layouts,
                         self.context).write()
                else:
                    path = os.path.abspath(root)
                    path = path.replace(os.path.abspath(self.BASE_DIR), '', 1)
                    path = path.lstrip(os.path.sep)
                    path = os.path.join(self.DEPLOY_DIR, path)
                    if not os.path.isdir(path):
                        os.makedirs(path)
                    shutil.copy(os.path.join(root, f), os.path.join(path, f))

    def serve(self, port):
        """ serve the deploy directory with an very simple, cgi
            capable web server on 0.0.0.0:<port>.
        """
        from BaseHTTPServer import HTTPServer
        from CGIHTTPServer import CGIHTTPRequestHandler
        os.chdir(self.DEPLOY_DIR)
        httpd = HTTPServer(('', int(port)), CGIHTTPRequestHandler)
        sa = httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    DEFAULT_PORT = 8080
    args = collections.deque(sys.argv[1:])

    serve = base = deploy = None
    while args and args[0].startswith('--'):
        arg = args.popleft()
        if arg.startswith('--serve'):
            serve = arg

    if args:
        base = args.popleft()
    else:
        print 'syntax: %s [options] <from> [to]\n' % sys.argv[0]
        print 'Options:'
        print '  --serve[:port]   Start web server (default port %s)\n' % DEFAULT_PORT
        sys.exit(1)

    if not os.path.isdir(base):
        print 'error: invalid directory: %s' % base
        sys.exit(2)

    if args:
        deploy = args.popleft()
    else:
        deploy = os.path.join(base, '_deploy')

    Config.updateconfig(base, deploy)
    site = Site()

    site.read()
    site.generate()
    site.deploy()

    if serve:
        port = DEFAULT_PORT
        if ':' in serve:
            serve, port = serve.split(':', 1)
        site.serve(port)
