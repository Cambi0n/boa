from events import *
from internalconstants import *

class Stores():
    def __init__(self, evManager, game):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        self.game = game
        
    def preparestores(self):
        #host only
        return None
        
        
    def Notify(self, event):
        pass

#        if isinstance( event, PrepareStoresEvent ):
#            self.preparestores()
        
