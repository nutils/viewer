#! /usr/bin/env python

#from finity import prop
import web, os, sys, re
import browser
import tempfile, zipfile, hashlib

# Specify the urls
urls = (
  '', 'Index',
  '/(index)?', 'Index',
  '/(index)/(.*)', 'Index',
  '/view.htm?(.*)', 'View',
  '/proxy/?(.*)', 'Proxy',
  '/zip/(.*)', 'DownloadZip',
  '/search/?(.*)', 'Search',
  '/(res|img|css|js|fonts)/(.*)', 'Resources'#,
  #'/(.*)', 'Data'
)

basedir = os.path.expanduser('~/public_html')


# ----------------------------------------
# Templates

class BasePage:

  def __init__( self ):
    self.render = web.template.render('templates', base='base')


""" INDEX
  Renders a table with an overview of all projects in the
  output directory
"""
class Index(BasePage):

  def GET( self, *args ):
    # Define a basepath
    projectdir = os.path.expanduser('~/public_html')

    # Get the subpath from the URL
    subpath = ''
    if len(args) > 1 and args[1] != '':
      subpath = args[1]

    # Get path segments
    subpathseg = subpath.split('/')

    # Do not allow paths into the log folder
    if len(subpathseg) > 4:
      subpathseg = subpathseg[0:4]
      subpath = '/'.join( subpathseg )

    # Get all the subfolders
    browse = browser.Projects( projectdir, subpath )
    projects = browse.overview()

    # Create a breadcrumb menu
    breadcrumb = []
    for i in range(len(subpathseg)):
      breadcrumb.append({
        'name': subpathseg[i],
        'url': '/'.join(subpathseg[:i+1])
      })


    return self.render.projects(projects=projects, breadcrumb=breadcrumb)

  def POST( self ):
    return self.GET( args )


class DownloadZip:
  def GET(self, *args):
    try:
      tmpdir = tempfile.gettempdir()
      tmpname = hashlib.md5('nutils-%s' % os.getpid() ).hexdigest() + '.zip'
      tmp = os.path.join( tmpdir, tmpname )
      path = '/home/rody/Documents/tue/templates/beamer'

      relpath = path.replace( os.path.realname(os.getcwd()), '' )
      return relpath
      zipf = zipfile.ZipFile(tmp, 'w')
      for root, dirs, files in os.walk(path):
        for fname in files:
          fpath = os.path.join(root, fname)
          zipf.write(os.path.join(root, fname))
      zipf.close()
      return tmp
    except:
      return web.notfound()

class View:
  def GET( self, *args ):
    try:
      fp = open('view.htm', 'r')
      return fp.read()
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    return self.GET( args )

""" RESOURCES
  Passes on the resources available in the folders img, css and js
"""
class Resources:
  def GET(self, media, fname):
    try:
      if media == 'res':
        fname = fname.replace('~','').replace('..','')
        rx = re.compile(r'[\\/]{2,}')
        fname = rx.sub(os.sep, fname)
        basename = os.path.expanduser('~/public_html')
        path = os.path.join( basename, fname )
      else:
        fname = os.path.basename(fname)
        path = os.path.join(media, fname)

      fp = open(path, 'r')
      return fp.read()
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    return self.GET( args )

""" PROXY
  Proxy server to fetch external files and pass them as local files, since ajax can only load local files.
"""
class Proxy:
  def GET(self, url):
    try:
      import urllib
      return urllib.urlopen( url ).read()
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    return self.GET( args )

if __name__ == "__main__":
  web.config.debug = True
  app = web.application(urls, globals())
  app.run()


