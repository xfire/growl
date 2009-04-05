growl - python based, easy extendable, blog aware, static site generator
========================================================================

growl is a static website generator, which is heavily inspired from
[jekyll](http://github.com/mojombo/jekyll/tree/master),
and which shameless stole some really cool ideas from jekyll. 

nevertheless growl brings some nice features:

* minimal dependencies
* easy to install (and use? ;])
* easy to extend

the [growl based site of my blog](http://github.com/xfire/downgrade/tree)
is also available on github.


installation
------------

### requisites

the following basic packages are needed:

    > apt-get install python python-yaml

all other is optional depending on you own needs.

I recommend to use [jinja2][jinja2] as templating engine. growl will 
use [jinja2][jinja2] as default, if it is installed.

    > apt-get install python-jinja2

you are free to use some other templating engine like [django][django],
[mako][mako] or [cheetah][cheetah]. for examples how to
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

* `--deploy`

  trigger deploy process. this do nothing per default, but you can
  add actions using hooks. (see `_hooks/deploy_rsync.py`)


input data
----------

growl will ignore all files and directories which starts with
a `.` or a `_`. (this can be changed via `Site.IGNORE`, see
[extending growl](#extending_growl))

all files ending with `_` or an transformer extension (`Config.transformers`)
are processed as **pages**. in that cases, the ending will be striped from
the filename. 

e.g.

* `index.html_`  ->  `index.html`
* `atom.xml_`  ->  `atom.xml`
* `somefile.txt.markdown`  ->  `somefile.txt`

some directories begining with an `_` are special to growl:

* `_deploy/` the default deploy directory
* `_layout/` contains your site layouts
* `_posts/` contains your posts
* `_hooks/` contains all your hooks (see [extending growl](#extending_growl))
* `_libs/` contains third party code (see [extending growl](#extending_growl))

all **pages** and **posts** optionally can have an [yaml][yaml] header. this
header must begin and end with a line containing 3 hyphen. e.g.

    ---
    layout: post
    title: my post title
    category: spam, eggs
    ---

all data defined in this header will be attached to the corresponding object
and can so accessed in your template code. an example in [jinja2][jinja2] may
look like

    <ul>
    {% for post in site.posts|reverse %}
        <li>{{ post.title }} - {{ post.date }}</li>
    {% endfor %}
    </ul>

in the context of your template, you have access to one or more of the following
objects.

### site

this holds the site wide informations.

* `site.now`

  current date and time when you run growl. this is a python
  [datetime](http://docs.python.org/library/datetime.html#datetime-objects) object.

    {{ site.now.year }}-{{site.now.month}}

* `site.posts`

  a chronological list of all posts.

    {% for post in site.posts|reverse|slice(8) %}
        {{ post.content }}
    {% endfor %}

* `site.unpublished_posts`

  a chronological list of all unpublished posts. e.g. all posts which set `publish` to
  false.

* `site.categories`

  a dictionary mapping category <-> posts.

    <ul>
    {% for cat in site.categories %}
        <li> <stong>{{ cat }}</strong>
            <ul>
                {% for post in site.categories.get(cat) %}
                    <li><a href="{{ post.url }}">{{ post.title }}</a> - {{ post.date }}</li>
                {% endfor %}
            </ul>
        </li>
    {% endfor %}
    </ul>

### page

* `page.url`

  the relative url to the page.

* `page.transformed`

  the transformed content. no layouts are applied here.

### post

* `post.date`

  a datetime object with the publish date of the post

* `post.url`

  the relative url to the post

* `post.publish`

  if set to false, the post will be generated, but is not in the list of `site.posts`. instead
  it's in the `site.unpublished_posts` list.

  if `publish` is not set, growl will assume this as true and the post will be normally published.

* `post.content`

  the transformed content. exactly the layout specified in the [yaml][yaml] header is applied.
  (no recursive applying)

* `post.transformed`

  the transformed content. no layouts are applied here.


<a name="extending_growl"/>
extending growl
---------------

growl is very easy extendable via python code placed in the `_hooks` and
`_libs` directory.

if the `_libs` directory exists, it is added to the python module search path
(`sys.path`). so python modules droped there, will be available in the code.

all files in the `_hooks` directory, which ends with `.py`, are executed
directly in the global scope of the growl.py file. thus a hook can freely
shape growls code at will. growl love that! ;)

here are some examples of what can be done. but you sure can imagine other
cool things.


### configuring template engines



### register new transformers

new transformers can be registered in the `Config` class by adding a
filename extension <-> transformation function mapping to the `transformers`
attribute. here an example for markdown2:

    import markdown2
    import functools

    Config.transformers['noop'] = lambda source: source
    Config.transformers['markdown2'] = functools.partial(
                markdown2.markdown,
                extras={'code-color': {"noclasses": True}})

the transformation function must return the transformed source text which is given
as the only parameter. so if you need to add more parameters to your
transformation function, best use the [functools](http://docs.python.org/library/functools.html)
module as you see in the example above.



### change which files will be ignored

growl decides to ignore files which filenames start with one of the tokens 
defined in `Site.IGNORE`. so a hook with the following content will make
growl to ignore all files begining with `.`, `_` and `foo`.

    Site.IGNORE += ('foo',)



### define global template context content

simply add your content to `Site.CONTEXT` like these examples:

    Site.CONTEXT.author = 'Rico Schiekel'
    Site.CONTEXT.site = AttrDict(author = 'Rico Schiekel')

note: `Site.CONTEXT.site` has to be an `AttrDict` instance!



### add some verbosity

as an example, we would display the currently processed post, while
growl chomp your input.

create a new file (e.g. `verbose.py`) in the `_hooks` directory with the
following content:

    def verbose_post_write(self):
        print 'post: %s - %s\n' % (self.date.strftime('%Y-%m-%d'), self.title)
        return verbose_post_write.super(self)
    Post.write = wrap(Post.write, verbose_post_write)

grows offers the helper function `wrap`, which wrap an existing function
of a class with a new one. to access the original function, use
`<new_function_name>.super(self, ...)` like in the example above.



bug reporting
-------------

please report bugs [here](http://bugs.projects.spamt.net/cgi-bin/bugzilla3/enter_bug.cgi?product=growl).


license
-------
[GPLv2](http://www.gnu.org/licenses/gpl-2.0.html)



  [jinja2]:  http://jinja.pocoo.org/2/          "jinja2"
  [django]:  http://www.djangoproject.com/      "django"
  [mako]:    http://www.makotemplates.org/      "mako"
  [cheetah]: http://www.cheetahtemplate.org/    "cheetah"
  [yaml]:    http://www.yaml.org/               "yaml"

