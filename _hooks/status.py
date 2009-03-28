#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys

def verbose_post_write(self):
    sys.stderr.write('post: %s\n' % self.title)
    return self._org_verbose_write()
Post._org_verbose_write = Post.write
Post.write = verbose_post_write

def verbose_page_write(self):
    sys.stderr.write('page: %s\n' % self.filename)
    return self._org_verbose_write()
Page._org_verbose_write = Page.write
Page.write = verbose_page_write


