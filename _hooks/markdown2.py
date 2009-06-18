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

"""
copy 'markdown2.py' from http://code.google.com/p/python-markdown2/
to _libs directory.
"""

import markdown2
import functools

Config.transformers['markdown2'] = functools.partial(
            markdown2.markdown,
            extras={'code-color': {"classes": True}})

Config.transformers['md2'] = Config.transformers['markdown2']
