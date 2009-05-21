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

import sys


@wrap(Post.write)
def verbose_post_write(forig, self):
    sys.stderr.write('post: %s - %s\n' %
                     (self.date.strftime('%Y-%m-%d'), self.title))
    return forig(self)


@wrap(Page.write)
def verbose_page_write(forig, self):
    sys.stderr.write('page: %s\n' % self.path)
    return forig(self)
