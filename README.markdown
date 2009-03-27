under construction...

growl - python based, easy extendable, blog aware, static site generator
========================================================================

growl is a static website generator, which is heavily inspired from
[jekyll](http://github.com/mojombo/jekyll/tree/master),
and which shameless stole some really cool ideas from jekyll. 

nevertheless growl brings some nice features:

* minimal dependencies
* easy to install (and use? ;])
* easy to extend


installation
------------

### requisites

the following basic packages are needed:

    > apt-get install python python-yaml

all other is optional depending on you own needs.

I recommend to use [jinja2](http://jinja.pocoo.org/2/) as templating
engine. growl will use jinja2 as default, if it is installed.

    > apt-get install python-jinja2

you are free to use some other templating engine like
[django](http://www.djangoproject.com/), [mako](http://www.makotemplates.org/)
or [Cheetah](http://www.cheetahtemplate.org/). for examples how to
configure them, see [extending growl](#extending_growl).

### finish the installation

after installing all needed packages, you can use `growl.py`
directly or copy it to a place which is in your `$PATH`.

    > ./growl.py ...
    > cp growl.py /usr/local/bin


usage
-----

simply call `growl.py` with the source directory:

    > growl.py my.site

growl will then generate the output in the directory `my.site/_deploy`.
if you want grow to spit the generated stuff into another directory,
simply specify this director as second parameter.

    > growl.py my.site /tmp/my.site.output

### options

* `--serve[:port]` (default port: 8080)

  generate the site to the deploy directory and then start a simple
  webserver. this is intended to be used for testing purposes only.


input data
----------

### files

### directories


<a name="extending_growl"/>
extending growl
---------------

* _hooks
* _libs

### configuring template engines

### register new transformers

### define global template context content

simply add your content to `Site.CONTEXT` like these examples:

    Site.CONTEXT.author = 'Rico Schiekel'
    Site.CONTEXT.site = AttrDict(author = 'Rico Schiekel')

note: `Site.CONTEXT.site` has to be an `AttrDict` instance!

### overwrite functions to change runtime behaviour

as an example, we would display the currently processed post, while
growl chomp your input.

create a new file (e.g. `verbose.py`) in the `_hooks` directory with the
following content:

    def verbose_write(self):
        print 'generating post: %s (from: %s)' % (self.title, self.filename)
        return self._org_verbose_write()

    Post._org_verbose_write = Post.write
    Post.write = verbose_write

as you see, we first safe the original write function of the class `Post`
under a new, unique name.

then we overwrite the original write function with our brand new, super
duper and much more verbose write function.

the new, verboser write function lately call the stored original function,
since we don't want to implement a new write behaviour.


license
-------
[GPLv2](http://www.gnu.org/licenses/gpl-2.0.html)
