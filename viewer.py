#! /usr/bin/env python

import web, os, sys, re
import browser, util
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
)


# Get configuration
conf = util.Settings()
conf.load('~/.nutilsrc')
conf['outdir'] = conf['outdir']

class BasePage:
  ''' BasePage
  Abstract page class
  '''

  def __init__( self ):
    ''' BasePage.__init__()
    Set up the templates for the viewer

    @return void
    '''
    self.render = web.template.render('templates', base='base')

  def POST( self, *args ):
    ''' BasePage.POST( [ args ] )
    Default to the GET behaviour when no POST is found

    @param list args
    @return string
    '''
    return self.GET( args )

class Index(BasePage):
  ''' Index
  Overview the projects in the viewer
  '''

  def GET( self, *args ):
    ''' Index.GET( [ args ] )
    Returns the page for a GET request

    @param list args
    @return string
    '''

    # Define a basepath
    projectdir = os.path.expanduser( conf['outdir'] )

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

class DownloadZip:
  ''' DownloadZip
  Page that serves a zip file of the requested project
  '''

  def GET(self, *args):
    ''' DownloadZip.GET( [ args ] )
    Returns the zip file on a GET request

    @param list args
    @return string
    '''
    try:
      tmpdir = tempfile.gettempdir()
      tmpname = hashlib.md5('nutils-%s' % os.getpid() ).hexdigest() + '.zip'
      tmp = os.sep.join([ tmpdir, tmpname ])
      return
      # TODO: path
      path = '/path/to/folder/to/make/zip'

      relpath = path.replace( os.path.realname(os.getcwd()), '' )
      return relpath
      zipf = zipfile.ZipFile(tmp, 'w')
      for root, dirs, files in os.walk(path):
        for fname in files:
          fpath = os.sep.join([ root, fname ])
          zipf.write(os.sep.join([root, fname ]))
      zipf.close()
      return tmp
    except:
      return web.notfound()

class View:
  ''' View
  Display the nutils viewer <view.htm>

  '''
  def GET( self, *args ):
    ''' View.GET( [ args ] )
    Returns the view.htm file on a GET request

    @param list args
    @return string
    '''
    try:
      fp = open('view.htm', 'r')
      return fp.read()
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    ''' VIEW.POST( url )
    Returns the resource on a POST request

    @param list args
    @return string
    '''
    return self.GET( args )

class Resources:
  ''' Resources
  Make res, img, css, js and fonts available
  '''

  def GET(self, media, fname):
    ''' Resources.GET( media, fname )
    Returns the resource file on a GET request

    @param string media
    @param string fname
    @return string
    '''
    try:
      if media == 'res':
        fname = fname.replace('~','').replace('..','')
        rx = re.compile(r'[\\/]{2,}')
        fname = rx.sub(os.sep, fname)
        basename = os.path.expanduser( conf['outdir'] )
        path = os.sep.join([ basename, fname ])
      else:
        fname = os.path.basename(fname)
        path = os.sep.join([ media, fname ])

      fp = open(path, 'r')
      return fp.read()
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    ''' Resources.POST( args )
    Returns the resource on a POST request

    @param list args
    @return string
    '''
    return self.GET( args )

class Proxy:
  ''' Proxy
  Proxy server to fetch external files and pass them
  as local files, since AJAX can only load local files.
  '''

  def GET(self, url):
    ''' Proxy.GET( url )
    Returns the resource on a GET request

    @param string url
    @return string
    '''
    try:
      import httplib

      # Request headers send
      headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0",
        "Cache-Control": "no-cache"
      }

      # Split url into protocol and address
      pos = url.find("://")
      if pos > -1 :
        prot = url[:pos]
        addr = url[(pos+3):]
      else:
        prot = "http"
        addr = url

      # Figure out the domain
      parts  = addr.split('/')
      domain = parts[0]
      query  = '/'.join(parts[1:])

      # Get the params
      pos = query.find('?')
      params = ''
      if pos > -1 :
        path = '/' + query[:pos]
        if pos+1 < len(query) :
          # Split into [name,value] array, append [''] if no value was supplied
          params = query[(pos+1):]
      else:
        path = '/' + query

      # Connect to the website
      conn = httplib.HTTPConnection( domain )
      conn.request("GET", path, params, headers )

      # Get the responce
      res = conn.getresponse()
      html = res.read()

      # Close connection
      conn.close()

      return html
    except:
      return web.notfound() # you can send an 404 error here if you want

  def POST( self, *args ):
    ''' Proxy.POST( args )
    Returns the resource on a POST request

    @param list args
    @return string
    '''
    return self.GET( args )

if __name__ == "__main__":
  web.config.debug = True
  app = web.application(urls, globals())
  app.run()
