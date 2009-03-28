#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

@templateFilter
def dateFormat(value, format='%d-%m-%Y'):
    return value.strftime(format)
