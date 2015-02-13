import Queue
import threading
#import pygame
#from pygame.locals import *

#from math import *
#from random import *

#from pgu import gui

from events import *
#from evmanager import *
#from game import *
#from controllers import *
#from mainview import *
#from unitview import *
from internalconstants import *
#from userconstants import *

#------------------------------------------------------------------------------

from copy import copy

class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""

    def __init__(self ):
        self.listeners = dict()
        self.eventQueue= []
        self.eventsListProcessed = 1

    #----------------------------------------------------------------------
    def Debug( self, ev):
        if debug_on:
#            if not isinstance( ev, UpdateViewEvent ) and not isinstance( ev, MouseoverEvent ):
            if not isinstance( ev, UpdateViewEvent ) and not isinstance( ev, MouseoverEvent ) \
                and not isinstance(ev, UpdateMap) and not isinstance(ev, ShowMovieFrame):
                print "   Message: " + ev.name
        else:
            return

    #----------------------------------------------------------------------
    def RegisterListener( self, listener, cats ):
        #if not hasattr( listener, "Notify" ): raise blah blah...
        for cat in cats:
            if cat not in self.listeners:
                self.listeners[cat]=[]
            self.listeners[cat].append(listener)

        # everybody gets events tagged as all
        if 'all' not in self.listeners:
            self.listeners['all']=[]
        self.listeners['all'].append(listener)

    #----------------------------------------------------------------------
    def UnregisterListener( self, listener ):
        if listener in self.listeners.keys():
            del self.listeners[ listener ]

    #----------------------------------------------------------------------
    def Post( self, event=None ):
    # basic logic
        # nothing happening
        # a pygame event (mouse or keyboard) occurs
        # handle everything that happens from that one pygame event before dealing with next pygame event
        # game event A generated
        # A generates game event B
        # notify everybody that deals with game event A before dealing with event B
        # handle event B, etc.
        # stay in cascade of game events until all done
        # handle 2nd pygame event

        '''if debug_on:
            if hasattr(event,"name"):
                if not isinstance( event, UpdateViewEvent ) and not isinstance( event, MouseoverEvent ) :
                    print("entered with " + event.name)'''

        while not queue.empty():
            ev = queue.get()
            self.Debug( ev )
            tlisteners = []
            for evcat in ev.catlist:
                for alistener in self.listeners[evcat]:
                    tlisteners.append(alistener)

            for listener in tlisteners:
                #print listener
                listener.Notify( ev )
                
            queue.task_done()

            '''if debug_on:
                if not isinstance( ev, UpdateViewEvent ) and not isinstance( ev, MouseoverEvent ) :
                    print("finished " + ev.name)'''


        '''if event:
            self.eventQueue.append( event )

        if self.eventsListProcessed:
            self.eventsListProcessed = 0
            self.events = copy( self.eventQueue )
            self.eventQueue = []
            while len(self.events) > 0:
                ev = self.events.pop(0)
                self.Debug( ev )

                tlisteners = []
                for evcat in ev.catlist:
                    for alistener in self.listeners[evcat]:
                        tlisteners.append(alistener)
#               uniqlisten = set(templisteners)
#               for listener in self.listeners.keys():
#               for listener in uniqlisten:
#               possibility of one listener receiving same event twice is not checked for!

#               best way, prepare ahead of time all the listeners for each event in a dict.
                for listener in tlisteners:
                    #print listener
                    listener.Notify( ev )

                if debug_on:
                    if not isinstance( ev, UpdateViewEvent ) and not isinstance( ev, MouseoverEvent ) :
                        print("finished " + ev.name)

            self.eventsListProcessed = 1

            # Take care of any game events that have been appended
            # as a result of dealing with original list of events.
            if len(self.eventQueue) != 0:
                self.Post()'''

