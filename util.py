import os

class Settings( dict ):

  def __init__( self ):
    ''' Settings.__init__()

    Initialize settings

    @return void
    '''
    self['outdir'] = '~/public_html'

  def load( self, fname ):
    ''' Settings.load( fname )

    Load a configuration file into this Settings
    object

    @param string fname
    @return dict properties

    '''
    if type( fname ) != str:
      raise Exception('No configuration file supplied')

    path = os.path.expanduser( fname )

    try:
      execfile( path, {}, self )
    except IOError:
      pass # file does not exist
