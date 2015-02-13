'''
Created on Aug 28, 2010

@author: bdf
'''

import os

from events import *

class SoundView:
    '''
    classdocs
    '''


    def __init__(self, evManager, mainview):
        '''
        Constructor
        '''
    
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        
        self.mainview = mainview
        
        self.assignSounds()
        
        
    def assignSounds(self):
     
        soundfilename ='whistledown.wav'
        pathsoundfn = os.path.join('data',soundfilename)
        self.whistledown = pygame.mixer.Sound(pathsoundfn)
        
        soundfilename ='battle013.wav'
        pathsoundfn = os.path.join('data',soundfilename)
        self.battle013 = pygame.mixer.Sound(pathsoundfn)
        self.battle013.set_volume(0.5)
        
        soundfilename ='scarynote.wav'
        pathsoundfn = os.path.join('data',soundfilename)
        self.scarynote = pygame.mixer.Sound(pathsoundfn)
        self.scarynote.set_volume(0.1)


    def Notify(self, event):
        if isinstance( event, PlaySound ):
            event.soundobject.play()
   