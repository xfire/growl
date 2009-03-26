growl - python based, easy extendable, blog aware, static site generator
========================================================================

growl is a static website generator, which is heavily inspired from
[jekyll](http://github.com/mojombo/jekyll/tree/master),
and which shameless stole some really cool ideas from jekyll. 

nevertheless growl brings some nice features:

* minimal dependencies
* easy to install (and use? :))
* easy to extend


installation
------------

the following basic packages are needed:

    apt-get install python-jinja2 python-yaml

all other is optional depending on you own needs.


usage
-----

simply call `growl.py` with the source directory:

    ./growl.py my.site

growl will then generate the output in the directory `my.site/_deploy`.
if you want grow to spit the generated stuff into another directory,
simply specify this director as second parameter.

    ./growl.py my.site /tmp/my.site.output

### options

* `--serve`


extending growl
---------------

* _hooks
* _libs


license
-------
[GPLv2](http://www.gnu.org/licenses/gpl-2.0.html)
