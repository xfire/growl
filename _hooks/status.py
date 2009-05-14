#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys

@wrap(Post.write)
def verbose_post_write(forig, self):
    sys.stderr.write('post: %s - %s\n' % (self.date.strftime('%Y-%m-%d'), self.title))
    return forig(self)

@wrap(Page.write)
def verbose_page_write(forig, self):
    sys.stderr.write('page: %s\n' % self.path)
    return forig(self)


