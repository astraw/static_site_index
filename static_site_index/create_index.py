#!/usr/bin/env python
import os, re, datetime, json

MY_DIR = os.path.split(__file__)[0]

JEKYLL_TEMPLATE="""---
layout: default
title: Index of {pathname}
---
<pre>{preformat_string}
<hr></pre>
"""


TEMPLATE="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of {pathname}</title>
  <script src="{site_root}js/angular.min.js"></script>
  <link rel="stylesheet" href="{site_root}css/bootstrap.min.css">
 </head>
 <body>
<h1>Index of {pathname}</h1>
<div id="html_index">
<pre>{preformat_string}
<hr></pre>
</div>

<div id="js_index">
{angular_template}
</div>

<script>
{json_data}
{js_file}
</script>
</body></html>
"""

def get_json_data(elements,parent_link):
    json_elements = elements[:] # copy
    if parent_link is not None:
        json_elements.insert(0,{
            'Name':'Parent Directory',
            'Link':parent_link,
            'Last_modified':None,
            'Size':None,
            })
    return json_elements

def get_html_table_buf(json_elements):
    columns = 'Name', 'Last_modified', 'Size'

    # establish minimum column widths
    widths = {}
    for colname in columns:
        widths[colname] = 4
    widths['Name']=32

    html_elements = []
    for element_data in json_elements:
        html_elements.append( element_data.copy() )

    title_dict = dict( [ (n,n) for n in columns ] )
    title_dict['Link'] = None
    html_elements.insert(0,title_dict)

    # find real widths
    for html_element_data in html_elements:
        if html_element_data['Last_modified'] is None:
            html_element_data['Last_modified'] = ''
        if html_element_data['Size'] is None:
            html_element_data['Size'] = '- '
        else:
            sz = html_element_data['Size']
            if isinstance(sz,int):
                html_element_data['Size'] = size_str(html_element_data['Size'])

        for colname in columns:
            widths[colname] = max(widths[colname],len(html_element_data[colname]))

    # write rows
    fmt_strs = []
    for colname in columns:
        if colname=='Size':
            align_char = '>'
        else:
            align_char = '<'
        this_col = '{%s:%s%d}'%(colname,align_char,widths[colname])
        if colname == 'Name':
            more = '<a href="{Link}">%s</a>'%this_col
            this_col = more
        fmt_strs.append( this_col )
    fmt_str = '      '+'  '.join(fmt_strs)
    rowbufs = []
    for rowidx,html_element_data in enumerate(html_elements):
        if rowidx==0:
            html_element_data['Link']=''
            linebuf = fmt_str.format(**html_element_data)
            linebuf = linebuf.replace('<a href="">','')
            lindebuf = linebuf.replace('</a>','')
            rowbufs.append( linebuf+'<hr>' )
        else:
            rowbufs.append( fmt_str.format(**html_element_data) )

    if 1:
        # remove linked spaces -----------
        rowbufs2 = []
        re_fix = re.compile( r'( +)</a>' )
        for row in rowbufs:
            rowbufs2.append( re_fix.sub( r'</a>\1', row ) )
        rowbufs = rowbufs2

    return '\n'.join(rowbufs)

def write_index(fname,elements,parent_link,pathname,jekyll=False):
    json_elements = get_json_data(elements,parent_link)
    json_data1 = 'var entries = {"files":'+json.dumps(json_elements)+'};'
    json_data2 = """
for (idx in entries.files) {
    var orig = entries.files[idx].Last_modified;
    if (orig!=null) {
        entries.files[idx].Last_modified = new Date(orig);
    }
}
"""
    json_data = json_data1 + json_data2

    preformat_string = get_html_table_buf(json_elements)

    depth = pathname.count('/')
    site_root = '/'.join( ['..']*depth ) + '/'

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

def size_str(insz):
    if insz>1e9:
        result = '%.1fG'%(insz/1e9,)
    elif insz>1e6:
        result = '%.1fM'%(insz/1e6,)
    elif insz>1e3:
        result = '%.1fK'%(insz/1e3,)
    else:
        result = '%d '%insz
    return result

def modtime_str(t):
    r = datetime.datetime.fromtimestamp(t)
    fmt = '%d-%b-%Y %H:%M'
    result = r.strftime(fmt)
    return result

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
            'Name':f,
            'Link':link,
            'Last_modified':modtime_str(mtime),
            'Size':sz,
            }
        if os.path.isdir(f):
            el['Name']=el['Name']+'/'
            el['type']='dir'
            el['Size']=None
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
    BASE_DIR='debs.strawlab.org'
    do_index(BASE_DIR,None,'/')
