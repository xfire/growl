#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

"""
copy 'markdown2.py' from http://code.google.com/p/python-markdown2/
to _libs directory.
"""

import markdown2
import functools

Config.transformers['markdown2'] = functools.partial(
            markdown2.markdown,
            extras={'code-color': {"noclasses": True}})
