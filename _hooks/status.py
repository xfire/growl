#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys

def verbose_post_write(forig, self):
    sys.stderr.write('post: %s - %s\n' % (self.date.strftime('%Y-%m-%d'), self.title))
    return forig(self)
Post.write = wrap(Post.write, verbose_post_write)

def verbose_page_write(forig, self):
    sys.stderr.write('page: %s\n' % self.path)
    return forig(self)
Page.write = wrap(Page.write, verbose_page_write)


