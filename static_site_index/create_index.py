#!/usr/bin/env python
from __future__ import print_function
import os, datetime, sys

INVALID=''

MY_DIR = os.path.split(__file__)[0]

JEKYLL_TEMPLATE="""---
layout: default
title: Index of {pathname}
---
{table_html}
"""


TEMPLATE="""<!DOCTYPE HTML>
<html>
 <head>
  <title>Index of {pathname}</title>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.2.19/angular.min.js"></script>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
 </head>
 <body>
<h1>Index of {pathname}</h1>
<div id="static_site_index_html_index">
{table_html}
</div>

<div id="static_site_index_js_index" style="display:none;visibility:hidden;">
{angular_template}
</div>

<div id="static_site_index_blurb">Page generated by <a href="https://github.com/astraw/static_site_index">github.com/astraw/static_site_index</a>.</div>

<script>
{js_file}
</script>
</body></html>
"""

def get_html_table_buf(html_elements):
    table_bufs = []
    table_bufs.append('<table id="static_site_index_html_table" class="table table-bordered">')
    table_bufs.append('<tr>' +
                      '<th>Name</th><th>Last modified</th><th>Size</th>' +
                      '</tr>')

    tab_fmt = ('<tr>'
               '<td><a href="{link}">{name}</a></td>'
               '<td>{lastmodified}</td>'
               '<td>{size}</td>'
               '</tr>')

    for html_element_data in html_elements:
        table_bufs.append(tab_fmt.format(**html_element_data))

    table_bufs.append('</table>')

    return '\n'.join(table_bufs)

def write_index(fname,elements,parent_link,pathname,jekyll=False):
    html_elements = [{
        'name':'.. (Parent Directory)',
        'link':parent_link,
        'lastmodified':INVALID,
        'size':INVALID,
        }] + elements

    table_html = get_html_table_buf(html_elements)

    index_js_fname = os.path.join(MY_DIR,'index.js')
    template_content_fname = os.path.join(MY_DIR,'template.html')
    js_file = open(index_js_fname,mode='r').read()

    # based on http://codepen.io/anon/pen/fjkcg
    angular_template = open(template_content_fname,mode='r').read()

    if jekyll:
        buf = JEKYLL_TEMPLATE.format( **locals() )
    else:
        buf = TEMPLATE.format( **locals() )
    with open(fname, mode='w') as fd:
        fd.write(buf)

def make_index(parent_link,pathname,jekyll=False,recursive=True):
    files = os.listdir(os.curdir)
    files.sort()
    elements = []
    for f in files:
        if f=='index.html':
            continue
        attrs = os.stat(f)
        mtime = attrs.st_mtime
        sz = attrs.st_size
        link = os.path.join( pathname, f )
        el = {
            'name':f,
            'link':link,
            'lastmodified':mtime,
            'size':sz,
            }
        if os.path.isdir(f):
            el['name']=el['name']+'/'
            el['type']='dir'
            el['size']=INVALID
            subdir = pathname + '/' + f
            if subdir.startswith('//'):
                subdir = subdir[1:] # trim leading double slash
            mdfile = os.path.join(f,'index.markdown')
            if not os.path.exists(mdfile):
                if recursive:
                    do_index(f, pathname, subdir, jekyll=jekyll, recursive=recursive)
        elif os.path.isfile(f):
            el['type']='file'
        else:
            raise ValueError('unknown dir entry: %r'%f)
        elements.append(el)
    write_index('index.html',elements,parent_link,pathname,jekyll=jekyll)

def do_index(filesystem_dirname, parent_link, this_url_path,jekyll=False,recursive=True):
    orig_dir = os.path.abspath(os.curdir)
    os.chdir( filesystem_dirname )
    try:
        make_index(parent_link, this_url_path,
                   jekyll=jekyll,
                   recursive=recursive)
    finally:
        os.chdir( orig_dir )

if __name__=='__main__':
    print('create_index called from command line')
    BASE_DIR = sys.argv[1]
    print('  BASE_DIR = %r'%BASE_DIR)
    do_index(BASE_DIR,None,'/')
