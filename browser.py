#! /usr/bin/env python

import os, re

#----------------------------------------

class File( object ):
  __SLOTS__ = ['name', 'file']
  name = ''
  path = ''

  def __init__( self, path ):
    self.name = os.path.basename( path )
    self.path = path

  def __str__( self ):
    return self.path

#----------------------------------------

class Folder( File ):
  __SLOTS__ = ['depth', 'children']
  depth = 0
  children = []

  def __init__( self, path, depth=0 ):
    self.name = os.path.basename( path )
    self.path = path
    self.depth = depth

  def contents( self, files=True ):
    if not os.path.isdir( self.path ):
      raise Exception % ('Path %s can not be scanned, this is not a folder' % self.path)

    lst = os.listdir( self.path )
    content = []

    for fname in lst:
      path = os.path.join( self.path, fname )

      if os.path.isdir( path ) and not os.path.islink( path ) :
        content.append( Folder( path, self.depth+1 ) )
      elif os.path.isfile( path ) and files:
        content.append( File( path ) )
      else:
        continue

    return content

  def buildtree( self, maxdepth=0, files=True ):
    # Stop when maxdepth is reached
    if maxdepth > 0 and self.depth >= maxdepth:
      return

    self.children = self.contents()

    for child in self.children:
      if type(child) == Folder:
        print str(child) + ' [' + str(child.depth) + ']'
        child.buildtree( maxdepth, files )

  def asciitree( self ):
    tree = ' '*self.depth + self.name + '\n'
    for child in self.children:
      tree += child.asciitree()
    return tree

#----------------------------------------

class Projects( Folder ):
  __SLOTS__     = ['basepath', 'curpath']
  __imgtypes__  = ['png', 'jpg', 'jpeg', 'gif']
  __retime__    = re.compile(r'^(\d{2}\-){2}\d{2}$')
  __reslashes__ = re.compile(r'[\\/]{2,}')

  basepath      = ''
  curpath       = ''

  def __init__( self, basepath, curpath, depth=0 ):
    # Store the separate paths to see
    # how many folders we are away from the base
    self.basepath = basepath
    self.curpath = curpath
    self.path = os.path.join(basepath, curpath)

    self.name = os.path.basename( curpath )
    self.depth = depth

  def overview( self ):
    """
    Projects.overview()

    Lists all the directories in the current directory
    It also looks up the last result and an image in the directory

    """
    # Get the files in the current directory
    files = os.listdir( self.path )
    results = []

    # Check out all the files found
    for fname in files:
      path = os.path.join( self.path, fname )

      # Find out whether there is a logfile
      logs = ['log.html', 'log.htm']
      haslog = False
      for log in logs:
        logfile = os.path.join( path, log )
        haslog  = os.path.isfile( logfile )
        if haslog == True:
          break

      # If this is a directory we assume it contains results
      if os.path.isdir( path ) and not os.path.islink( path ) :
        res = {
          'name': fname,
          'path': os.path.join(self.curpath, fname),
          'haslog': haslog,
          'img': self.findimage( fname ),
          'lastchanged': self.lastchanged( fname )
        }

        results.append( res )

    return results

  def findimage( self, subpath, topdown=False ):
    """
    Projects.findimage( subpath, [ topdown ] )

    Find an image in <current path>/<subpath>

    @param string subpath   Where to look for the image?
    @param bool topdown     Look in opposite direction
    @return string path     The image path

    """
    # Where are we looking right now
    location = os.path.join( self.path, subpath )

    for root, dirs, files in os.walk( location, topdown=topdown):
      for fname in files:
        subpath = os.path.join( root, fname )

        # Check if this is an image
        lowerpath = subpath.lower()
        for ext in self.__imgtypes__:
          if lowerpath.endswith('.' + ext):
            return subpath

    # Found nothing
    return False

  def lastchanged( self, subpath ):
    """
    Projects.findimage( subpath )

    Find the folder containing the last simulation

    @param string subpath       Where to look for the image?
    @return tuple lastchanged   The image path

    """
    # Where are we looking right now
    location = os.path.join( self.path, subpath )

    # Clean double slashes and slashes at the beginning and end
    basepath = self.basepath.strip('/').strip('\\')
    basepath = self.__reslashes__.sub( os.path.sep, basepath )

    for root, dirs, files in os.walk( location, topdown=True):
      # Clean double slashes and slashes at the beginning and end
      path = self.__reslashes__.sub( os.path.sep, root )
      path = path.replace( basepath, '' )# Subtract base
      path = path.strip('/').strip('\\')# No slashes at start or end
      path = path.split( os.path.sep )

      # See how many folders we have
      # (we require 5 to get the full path)
      # <project>/<year>/<month>/<date>/<time>
      depth = len(path)
      if depth == 5:
        return tuple(path[1:])


    # Not found
    return None # ['00','00','0000','00-00-00']
