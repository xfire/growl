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


def wrap(orig_func, new_func, name = 'super'):
    """ helper function to wrap an existing function of a class.
        e.g.
    
        def verbose_write(self):
            print 'generating post: %s (from: %s)' % (self.title, self.filename)
            return verbose_write.super(self)
        Post.write = wrap(Post.write, verbose_write)
    
        the original function will be available as <new_function_name>.super.
    """

    @functools.wraps(orig_func)
    def wrapper(*args, **kwargs):
        setattr(new_func, name, orig_func)
        return new_func(*args, **kwargs)
    return wrapper


class AttrDict(dict):
    """ dictionary which provides its items as attributes.
    """

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def copy(self):
        return AttrDict(super(AttrDict, self).copy())


class Config(object):
    """ base class providing some static configuration values.
    """

    @classmethod
    def updateconfig(cls, base, deploy):
        cls.transformers = {}
        cls.BASE_DIR = base
        cls.DEPLOY_DIR = deploy
        cls.LAYOUT_DIR = os.path.join(base, '_layout')
        cls.POST_DIR = os.path.join(base, '_posts')
        cls.HOOK_DIR = os.path.join(base, '_hooks')
        cls.LIB_DIR = os.path.join(base, '_libs')
        cls.POST_FILE_EXT = '.html'


class Template(Config):
    """ abstract template base class providing support for an
        yaml header, transforming based on file extension,
        rendering (only using current layout if defined) and 
        layouting (applying all layouts).
    """

    RE_YAML = re.compile(r'(^---\s*$(?P<yaml>.*?)^---\s*$)?(?P<content>.*)',
                         re.M | re.S)

    def __init__(self, filename, layouts, context):
        super(Template, self).__init__()
        self.filename = filename
        self.layouts = layouts
        self.context = context.copy()
        self.context.layout = None
        self.read_yaml()

    def read_yaml(self):
        """ read yaml header and remove the header from content
        """
        self._content = file(self.filename, 'r').read()

        mo = self.RE_YAML.match(self._content)
        if mo and mo.groupdict().get('yaml'):
            self.context.update(yaml.load(mo.groupdict().get('yaml')))
            self._content = mo.groupdict().get('content')

    def transform(self):
        """ do transformation based on filename extension.
            e.g. do markdown or textile transformations
        """
        ext = os.path.splitext(self.filename)[-1][1:]
        t = self.transformers.get(ext, lambda x: x)
        return t(self._content)

    def render(self):
        """ render content, so transforming and then
            apply current layout.
        """
        ctx = self.context.copy()
        ctx.content = renderTemplate(self.transform(), ctx)
        layout = self.layouts.get(ctx.layout)
        if layout:
            return renderTemplate(layout.content, ctx)
        else:
            return ctx.content

    def layout(self):
        """ layout content, so transforming and then applying
            all layouts.
        """
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
        """ write content to path in deploy directory.
        """
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

    @property
    def transformed(self):
        return self.transform()


class Layout(Template):
    """ a layout template from _layouts/ directory.
    """

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
    """ a page template which should be transformed. e.g. files which
        filename ends with an '_' or an transformer file extension.
    """

    TRANSFORM = ('_', )

    def __init__(self, filename, layout, context):
        super(Page, self).__init__(filename, layout, context)

        self.context.page = self

    @property
    def url(self):
        return self.path.replace(os.path.sep, '/')

    @property
    def path(self):
        path = os.path.abspath(self.filename)
        npath, ext = os.path.splitext(path)
        if self.filename[-1] in Page.TRANSFORM:
            path = path[:-1]
        elif ext and ext[1:] in self.transformers:
            path = npath
        path = path.replace(os.path.abspath(self.BASE_DIR), '', 1)
        return path.lstrip(os.path.sep)

    @property
    def content(self):
        return self.render()

    def write(self):
        return super(Page, self).write(self.path, self.layout())

    @staticmethod
    def transformable(filename):
        """ return true, if the file is transformable. that means the
            filename ends with a character from self.TRANSFORM or
            self.transformers.
        """
        ext = os.path.splitext(filename)[-1]
        return ((filename[-1] in Page.TRANSFORM) or
                (ext and ext[1:] in Page.transformers))


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

    def __cmp__(self, other):
        return cmp(self.date, other.date)


class Site(Config):
    """ controls the site and holds the global context object. the context
        object contains all layouts, all posts and categories.
        hooks can be used to configure the context.
    """

    CONTEXT = AttrDict()
    IGNORE = ('_', '.')

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
        """ load all available hooks from the _hooks/ directory.
        """
        if os.path.isdir(self.HOOK_DIR):
            for f in sorted(self.ignoreFilter(os.listdir(self.HOOK_DIR))):
                if f.endswith('.py'):
                    execfile(os.path.join(self.HOOK_DIR, f), globals())

    def read(self):
        """ read all layouts and posts and calculate the categories.
        """
        self.read_layouts()
        self.read_posts()
        self.calc_categories()

    def generate(self):
        """ write all posts and then the site content to the deploy directory.
        """
        self.write_posts()
        self.write_site_content()

    def deploy(self):
        """ empty deply function which can be used by hooks to deploy the
            generated site. e.g. rsync to the webserver, ...
        """
        pass

    def read_layouts(self):
        if os.path.isdir(self.LAYOUT_DIR):
            self.layouts = [Layout(os.path.join(self.LAYOUT_DIR, f),
                                   self.context)
                                for f in self.ignoreFilter(os.listdir(
                                                            self.LAYOUT_DIR))]
            self.layouts = dict((l.name, l) for l in self.layouts)

    def read_posts(self):
        if os.path.isdir(self.POST_DIR):
            self.posts = [Post(os.path.join(self.POST_DIR, f),
                               self.layouts,
                               self.context)
                              for f in self.ignoreFilter(os.listdir(
                                                            self.POST_DIR))]
            self.context.site.posts = sorted(self.posts)

    def calc_categories(self):
        self.categories = AttrDict()
        for post in self.posts:
            for cat in post.categories:
                self.categories.setdefault(cat, []).append(post)
            if not post.categories:
                self.categories.setdefault(None, []).append(post)
        self.context.site.categories = self.categories

    def write_posts(self):
        for p in self.posts:
            p.write()

    def write_site_content(self):
        """ copy site content to deploy directory.

            ignoring all files and directories, if their filename
            begins with a token defined in IGNORE.

            files with and filename ending with an token defined in
            TRANSFORM are transformed via the Page class. all other
            files are simple copied.
        """

        for root, dirs, files in os.walk(self.BASE_DIR):
            base = root.replace(self.BASE_DIR, '')
            base = base.lstrip(os.path.sep)

            for d in self.ignoreFilter(dirs):
                nd = os.path.join(self.DEPLOY_DIR, base, d)
                if not os.path.isdir(nd):
                    os.makedirs(nd)
            dirs[:] = self.ignoreFilter(dirs)

            for f in self.ignoreFilter(files):
                if Page.transformable(f):
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

    def ignoreFilter(self, seq):
        """ filter out files starting with self.IGNORE tokens
        """

        def ignore_filter(item):
            for ign in self.IGNORE:
                if item.startswith(ign):
                    return False
            return True
        return itertools.ifilter(ignore_filter, seq)


if __name__ == '__main__':
    DEFAULT_PORT = 8080
    args = collections.deque(sys.argv[1:])

    serve = base = deploy_path = None
    deploy_site = False

    while args and args[0].startswith('--'):
        arg = args.popleft()
        if arg.startswith('--serve'):
            serve = arg
        elif arg.startswith('--deploy'):
            deploy_site = True

    if args:
        base = args.popleft()
    else:
        print 'syntax: %s [options] <from> [to]\n' % sys.argv[0]
        print 'Options:'
        print '  --serve[:port]   Start web server',
        print '(default port %s)\n' % DEFAULT_PORT
        sys.exit(1)

    if not os.path.isdir(base):
        print 'error: invalid directory: %s' % base
        sys.exit(2)

    if args:
        deploy_path = args.popleft()
    else:
        deploy_path = os.path.join(base, '_deploy')

    Config.updateconfig(base, deploy_path)

    try:
        import markdown
        Config.transformers['markdown'] = markdown.markdown
    except ImportError:
        pass

    try:
        import textile
        Config.transformers['textile'] = textile.textile
    except ImportError:
        pass

    site = Site()

    site.read()
    site.generate()
    if deploy_site:
        site.deploy()

    if serve:
        port = DEFAULT_PORT
        if ':' in serve:
            serve, port = serve.split(':', 1)
        site.serve(port)
