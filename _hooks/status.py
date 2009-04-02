#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys

def verbose_post_write(self):
    sys.stderr.write('post: %s - %s\n' % (self.date.strftime('%Y-%m-%d'), self.title))
    return verbose_post_write.super(self)
Post.write = wrap(Post.write, verbose_post_write)

def verbose_page_write(self):
    sys.stderr.write('page: %s\n' % self.path)
    return verbose_page_write.super(self)
Page.write = wrap(Page.write, verbose_page_write)


