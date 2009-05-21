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


@templateFilter
def dateFormat(dt, format='%Y-%m-%d'):
    return dt.strftime(format)


@templateFilter
def xmldatetime(dt):
    """ shameless stolen from http://github.com/lakshmivyas/hyde
        thanks alot
    """
    zprefix = "Z"
    tz = dt.strftime("%z")
    if tz:
        zprefix = tz[:3] + ":" + tz[3:]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + zprefix


@templateFilter
def xtruncate(s, length=255, end='...'):
    import tidy

    options = dict(output_xhtml=1,
                   add_xml_decl=1,
                   indent=1,
                   show_body_only=1,
                   tidy_mark=0)
    return str(tidy.parseString(str(s[:length]) + end, **options))
