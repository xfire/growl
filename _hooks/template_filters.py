#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

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

