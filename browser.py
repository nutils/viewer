#! /usr/bin/env python

import os, re

class File( object ):
  name = ''
  path = ''

  def __init__( self, path ):
    self.name = os.path.basename( path )
    self.path = path

  def __str__( self ):
    return self.path

class Folder( File ):
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

class Projects( Folder ):
  __imgtypes__ = ['png', 'jpg', 'jpeg', 'gif']
  __retime__ = re.compile(r'^(\d{2}\-){2}\d{2}$')

  def overview( self ):
    files = os.listdir( self.path )
    projects = []
    for fname in files:
      path = os.path.join( self.path, fname )
      if os.path.isdir( path ) and not os.path.islink( path ) :
        project = { \
          'name': fname, \
          'img': self.findimage( fname ), \
          'lastchanged': self.lastchanged( fname ) \
        }
        projects.append( project )
    return projects

  def findimage( self, projectpath, imgpath='' ):
    path = os.path.join( self.path, projectpath, imgpath )
    files = os.listdir( path )
    files.sort()

    for fname in files:
      subpath = os.path.join( path, fname )
      if os.path.isdir( subpath ) and not os.path.islink( subpath ):
        # If an image was found in one of the folders return it
        newimgpath = os.path.join( imgpath, fname)
        result = self.findimage( projectpath, newimgpath )
        if result != False:
          return result
      elif os.path.isfile( subpath ) and not os.path.islink( subpath ):
        # Check if this is an image
        lowerpath = subpath.lower()
        for ext in self.__imgtypes__:
          if lowerpath.endswith('.' + ext):
            newimgpath = os.path.join( projectpath, imgpath, fname)
            return newimgpath

    # Found nothing
    return False

  def lastchanged( self, projectpath ):
    folders = []

    # Try to find the last /year/month/day/time path for the project
    for i in range(4):
      path = os.sep.join( [self.path, projectpath] + folders )

      if not os.path.isdir( path ):
        continue

      files = os.listdir( path )
      files.sort()
      cnt = len(files)

      # Start looking for the last date/time folder
      for j in range(cnt-1, -1, -1):
        # folders year, month and date may only contian digits
        if i < 3 and not files[j].isdigit():
          continue

        # Time folder should match regex pattern self.__retime__
        if i == 3 and self.__retime__.match(files[j]) == None:
          continue

        # Found the last folder
        folders.append( files[j] )
        break

    return folders


# homepath = os.path.expanduser('~/public_html')
# homefolder = Folder( homepath )
# print homefolder.contents()
# homefolder.buildtree( maxdepth=6, files=False )
