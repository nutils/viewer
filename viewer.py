#! /usr/bin/env python

#from finity import prop
import web, os, sys, re
import browser

# Specify the urls
urls = (
  '/(index)?/?', 'Index',
  '/index/(.*)', 'Index',
  '/view/?(.*)', 'View',
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
    projectdir = os.path.expanduser('~/public_html')
    browse = browser.Projects( projectdir)
    print args
    projects = browse.overview()
    return self.render.projects(projects=projects)

  def POST( self ):
    return 'Hello World'

class View:
  def GET( self, args ):
    try:
      fp = open('view.htm', 'r')
      return fp.read()
    finally:
      return web.notfound() # you can send an 404 error here if you want

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

if __name__ == "__main__":
  web.config.debug = True
  app = web.application(urls, globals())
  app.run()


