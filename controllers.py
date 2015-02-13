import Queue
import sys

import pygame
from pygame.locals import *

from math import *
#from random import *

from twisted.internet import reactor
from twisted.internet import task

#from pgu import gui

from events import *
from evmanager import *
from game import *
from mainview import *
from unitview import *
from internalconstants import *
from userconstants import *
import random
from clientroundresults import *
import hostgamecalcs as hgc


#------------------------------------------------------------------------------
class MainMapController:
    """..."""
    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
        self.scrollctr = 0
        self.alloworders = 1
        self.drawingSelectRect = False
        self.startRectPos = None
        self.endRectPos = None

    #----------------------------------------------------------------------
    def HandleTimerEvent(self):
        self.pguapp.doTimerFuncs()
        ev = None

        if pygame.mouse.get_focused():
            mousepos = pygame.mouse.get_pos()
            
            if pygame.mouse.get_pressed()[0]:
                if self.view.minimaprect.collidepoint(mousepos):
                    newrectreq = self.view.mapRect.move(0,0)
                    newrectreq.center = self.view.convertMiniMapVSPixToVSPix( (mousepos[0] - self.view.minimaprect.left , mousepos[1] - self.view.minimaprect.top) )
                    ev = MapMoveRequest(newrectreq.topleft)
            else:
                if not self.view.innerrect.collidepoint(mousepos):
                    self.scrollctr += 1
                    if self.scrollctr > scroll_slowdown:
                        self.scrollctr = 0
                        if mousepos[0] <= scroll_width:
                            scrolldir = DIRECTION_LEFT
                        elif self.view.mainscrsize[0]-mousepos[0] <= scroll_width:
                            scrolldir = DIRECTION_RIGHT
                        elif mousepos[1] <= scroll_width:
                            scrolldir = DIRECTION_UP
                        elif self.view.mainscrsize[1]-mousepos[1] <= scroll_width:
                            scrolldir = DIRECTION_DOWN
    
                else:
                    ev = MouseoverEvent(mousepos)


        if ev:
            queue.put(ev)

    #----------------------------------------------------------------------
    def HandlePyGameEvent(self, event):
        ev = None
        skip_click = False
        
#        print 'controller, main, pygamer', event
        self.pguapp.event(event)

        if event.type == KEYDOWN:
            print 'controller, main, keydown'
            if event.key == K_s and self.view.selectedSprite and self.alloworders:
                if self.view.selectedSprite.type == 'city':
                    ev = showSupplyPopUpEvent(self.view.selectedSprite.object)
                    print 'controller. main, s hit', threading.currentThread()
            elif event.key == K_ESCAPE:
                ev = QuitEvent()
            elif event.key == K_SPACE and self.view.selectionContains['mynationunits']:
                print 'space2'
                ev = UmpuVisChange()
                    
        elif event.type == KEYUP:
            print 'controller, main, keyup'
            if event.key == K_F1:
                pass
            elif event.key == K_BACKSPACE and self.view.selectedSprite:
                if self.alloworders:
                    if hasattr(self.view.selectedSprite,'object'):
                        if self.view.selectedSprite.object.name in self.view.game.playerschars[self.view.game.myprofname]:
                            ev = DeleteLastOrderForSelectedSprite(self.view.selectedSprite)
                    
            elif event.key == K_ESCAPE:
                if self.view.primary_floating_menu_rect:
                    ev = HidePrimaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = HideSecondaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = None

        elif event.type == MOUSEBUTTONDOWN:
            print 'mousebuttondown'
            if self.view.primary_floating_menu_rect:
                if self.view.primary_floating_menu_rect.collidepoint(event.pos):
                    skip_click = True
                else:
                    if self.view.secondary_floating_menu_rect:
                        if self.view.secondary_floating_menu_rect.collidepoint(event.pos):
                            skip_click = True
                if not skip_click:
                    ev = HidePrimaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = HideSecondaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = None
            if not skip_click:
                if event.button == 1:
                    if self.view.minimaprect.collidepoint(event.pos):
                        newrectreq = self.view.mapRect.move(0,0)
                        newrectreq.center = self.view.convertMiniMapVSPixToVSPix( (event.pos[0] - self.view.minimaprect.left , event.pos[1] - self.view.minimaprect.top) )
                        ev = MapMoveRequest(newrectreq.topleft)
            if not skip_click:        
                if event.button == 4:
                    if self.view.mapViewPortRect.collidepoint(event.pos):
                        ev = MapZoomRequest(0, event.pos)    # zooming in
    
                elif event.button == 5:
                    if self.view.mapViewPortRect.collidepoint(event.pos):
                        ev = MapZoomRequest(1, event.pos)    # zooming out
                    
        elif event.type == MOUSEBUTTONUP:
            if self.view.primary_floating_menu_rect:
                if self.view.primary_floating_menu_rect.collidepoint(event.pos):
                    skip_click = True
            if self.view.secondary_floating_menu_rect:                
                if self.view.secondary_floating_menu_rect.collidepoint(event.pos):
                    skip_click = True
            if not skip_click:
                if event.button == 1:
                    if self.view.mapViewPortRect.collidepoint(event.pos) and not self.drawingSelectRect:
                        keymods = pygame.key.get_mods()
                        ev = MapLeftClickEvent(event.pos, keymods & KMOD_SHIFT)
                    elif self.view.selectionwinrect.collidepoint(event.pos):
                        keymods = pygame.key.get_mods()
                        ev = SelectionWindowLeftClickEvent(event.pos, keymods & KMOD_SHIFT)
                                
    
                elif event.button == 3:
                    if self.alloworders:
                        if self.view.mapInMapViewPortRect[self.view.zoomlevel].collidepoint(event.pos):
                            keymods = pygame.key.get_mods()
                            ev = MapRightClickEvent(event.pos, keymods)
                        elif self.view.selectionwinrect.collidepoint(event.pos):
                            keymods = pygame.key.get_mods()
                            ev = SelectionWindowRightClickEvent(event.pos,keymods)
                            
                        elif self.view.minimaprect.collidepoint(event.pos): # todo, fix so can't click outside map (actual terrain) in minimap
                            ev = MiniMapRightClickEvent(event.pos)

        elif event.type == SHOW_MOVIEFRAME:
            ev = ShowMovieFrame()

        if ev:
            queue.put(ev)

class PopUpController:
    """wxPython will handle the clicks inside the wx.Panel pop up.  
    This handles clicks outside the panel"""
    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
        self.alloworders = 1
        
    def HandleTimerEvent(self):
        ev = None

    def HandlePyGameEvent(self, event):
        ev = None
        self.pguapp.event(event)
        
        if event.type == KEYDOWN:
            print 'space3'
            if (event.key == K_ESCAPE or event.key == K_SPACE) and self.view.selectionContains['mynationunits']:
                #pass
                print 'space4'
                eV = UmpuVisChange()
                queue.put(eV)
        

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
#                if self.view.mapViewPortRect.collidepoint(event.pos):
#                    ev = MapLeftClickEvent(event.pos, self.pursuemode)
                if self.view.selectionwinrect.collidepoint(event.pos):
                    ev = SelectionWindowLeftClickEvent(event.pos,0)
                            
        if ev:
            queue.put(ev)


class CitySupplyPopUpController:
    """wxPython will handle the clicks inside the wx.Frame pop up.  
    This handles clicks outside the frame"""
    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
        self.alloworders = 1
#        self.citysupplymode = False
        self.addingToRoute = False
        
    def HandleTimerEvent(self):
        self.pguapp.doTimerFuncs()
        ev = None

    def HandlePyGameEvent(self, event):
        ev = None
        self.pguapp.event(event)
        
        if event.type == KEYDOWN:
            print 's 3'
#            if event.key == K_ESCAPE:
#                ev = QuitEvent()
            if (event.key == K_s or event.key == K_ESCAPE):
                #pass
                print 's 4'
                eV = hideSupplyPopUpEvent()
                queue.put(eV)
                
        elif event.type == MOUSEBUTTONUP:
            print 'citysupplycontroller'
            if event.button == 3 and self.addingToRoute:
                if self.view.mapInMapViewPortRect[self.view.zoomlevel].collidepoint(event.pos):
                    mappos = self.view.convertWholeViewPortPixToMapPos(event.pos)
                    ev = addSupplyRouteSection(mappos, self.view.selectedSprite.object, self.view.cv.highlightedRouteNum)

        if ev:
            queue.put(ev)

class ModalWindowController:
    """A pgu window is the only thing that can receive mouse actions"""
    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
        self.window_ref = None
        self.drag_in_progress = False
        
    def HandleTimerEvent(self):
        pass

    def HandlePyGameEvent(self, event):
        if event.type == MOUSEBUTTONUP:
            print '**************controllers**********',event.type, self.window_ref.rect, pygame.mouse.get_pos(), self.window_ref.rect.collidepoint(pygame.mouse.get_pos()) 
        floating_menu_hit = False
        if pygame.mouse.get_focused():
            mousepos = pygame.mouse.get_pos()
            if self.view.primary_floating_menu_rect:
                if self.view.primary_floating_menu_rect.collidepoint(mousepos):
                    floating_menu_hit = True
                elif self.view.secondary_floating_menu_rect:                
                    if self.view.secondary_floating_menu_rect.collidepoint(mousepos):
                        floating_menu_hit = True
                if floating_menu_hit:
                    self.pguapp.event(event)
                elif event.type == MOUSEBUTTONUP:
                    ev = HidePrimaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = HideSecondaryFloatingMenuEvent()
                    queue.put(ev)
            elif self.window_ref:
                if self.window_ref.rect.collidepoint(mousepos) \
                or (self.drag_in_progress and event.type == MOUSEMOTION):
                    self.pguapp.event(event)


        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                if self.view.primary_floating_menu_rect:
                    ev = HidePrimaryFloatingMenuEvent()
                    queue.put(ev)
                    ev = HideSecondaryFloatingMenuEvent()
                    queue.put(ev)
                else:
                    ev = HideModalWindowEvent()
                    queue.put(ev)
#                ev = SwitchToMainMapControllerEvent()
#                queue.put(ev)


class ChooseTargetController:
    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
#        self.msg = None
#        self.source = None
#        self.validate_func = None
#        self.chosen_func = None
        self.msg_window_ref = None
        self.cancel_func = None
        
    def HandleTimerEvent(self):
        self.pguapp.doTimerFuncs()
        msg_window_hit = False
        if pygame.mouse.get_focused():
            mousepos = pygame.mouse.get_pos()
            if self.msg_window_ref:
                if self.msg_window_ref.rect.collidepoint(mousepos):
                    msg_window_hit = True
            if not msg_window_hit:
                buttons_pressed = pygame.mouse.get_pressed() 
                if buttons_pressed[0]:
                    if self.view.minimaprect.collidepoint(mousepos):
                        newrectreq = self.view.mapRect.move(0,0)
                        newrectreq.center = self.view.convertMiniMapVSPixToVSPix( (mousepos[0] - self.view.minimaprect.left , mousepos[1] - self.view.minimaprect.top) )
                        ev = MapMoveRequest(newrectreq.topleft)
                        queue.put(ev)
                elif not buttons_pressed[1] and not buttons_pressed[2]:
                    ev = MouseoverEvent(mousepos)
                    queue.put(ev)
                        

    def HandlePyGameEvent(self, event):
        msg_window_hit = False
        if pygame.mouse.get_focused():
            mousepos = pygame.mouse.get_pos()
            if self.msg_window_ref:
                if self.msg_window_ref.rect.collidepoint(mousepos) \
                or (self.msg_window_ref._draginprogress and event.type == MOUSEMOTION):
                    msg_window_hit = True
                    self.pguapp.event(event)

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                self.cancel_func()
#                self.pguctrl.hide_nonmodal_popup()
#                ev = SwitchToMainMapControllerEvent()
#                queue.put(ev)
                
        if not msg_window_hit:
            
            if event.type == MOUSEBUTTONDOWN:
                print 'mousebuttondown'
                if event.button == 1:
                    if self.view.minimaprect.collidepoint(event.pos):
                        newrectreq = self.view.mapRect.move(0,0)
                        newrectreq.center = self.view.convertMiniMapVSPixToVSPix( (event.pos[0] - self.view.minimaprect.left , event.pos[1] - self.view.minimaprect.top) )
                        ev = MapMoveRequest(newrectreq.topleft)
                        queue.put(ev)
                elif event.button == 4:
                    if self.view.mapViewPortRect.collidepoint(event.pos):
                        ev = MapZoomRequest(0, event.pos)    # zooming in
                        queue.put(ev)
                elif event.button == 5:
                    if self.view.mapViewPortRect.collidepoint(event.pos):
                        ev = MapZoomRequest(1, event.pos)    # zooming out
                        queue.put(ev)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 3:
                    print 'mousebuttonup'
#                    if self.alloworders:
                    if self.view.mapInMapViewPortRect[self.view.zoomlevel].collidepoint(event.pos):
                        print 'mousebuttonup and in map'
                        keymods = pygame.key.get_mods()
                        ev = MapRightClickEvent(event.pos, keymods, target_mode = True)
                        queue.put(ev)
            

class PguOnlyController:

    def __init__(self, evManager, view, pguapp):
        self.evManager = evManager
#       self.evManager.RegisterListener( self )
        self.view = view
        self.pguapp = pguapp
#        self.alloworders = 1
#        self.pursuemode = False
        
    def HandleTimerEvent(self):
        pass

    def HandlePyGameEvent(self, event):
#        print 'controllers', event
        self.pguapp.event(event)

#------------------------------------------------------------------------------
class MasterController:
    """..."""
    def __init__(self, evManager, view, pguapp, pguctrl):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

        self.mainmapC = MainMapController(evManager, view, pguapp)
        self.popupC = PopUpController(evManager, view, pguapp)
        self.citysupplyPopupC = CitySupplyPopUpController(evManager, view, pguapp)
        self.pgu_only_c = PguOnlyController(evManager, view, pguapp)
        self.modal_window_c = ModalWindowController(evManager, view, pguapp)
        self.choose_target_c = ChooseTargetController(evManager, view, pguapp)

#       self.guiClasses = { 'start': [BasicController],
#                           'options': [BasicController],
#                           'mainmap': [MainMapController],
#                           'minimap': [MiniMapController],
        self.guiClasses = { 'mainmap': self.mainmapC,
                            'popup': self.popupC,
                            'citysupplypopup': self.citysupplyPopupC,
                            'pguonly': self.pgu_only_c,
                            'modalwindow': self.modal_window_c,
                            'choose_target': self.choose_target_c
                          }
#        self.SwitchController( 'mainmap' )
        self.SwitchController( 'pguonly' )

        self.keepGoing = 1
        self.endgame = 0
        self.newmc = 0
        self.runninggame = 0

        self.finishedSoFar = []
        self.hostCheckedIn = 0
        self.view = view
        self.pguapp = pguapp
        self.pguctrl = pguctrl

        self.view.sendControllerRefToView(self)
        
        self.timerinterval = float(timerspeed)/float(1000)
        
#        self.timed_event_list = []
        
        self.free_move_update_interval = 100    # real time (in ms) that pass between game updates.
                                                # game time might pass slower or faster depending
                                                # on self.game_speed
        self.in_free_move_mode = True
        self.my_clock = None
        self.game_speed = 1
        self.time_since_last_game_update = 0
        # Note: be sure to use float, else a timerinterval of 0 may result,
        # which would use lots of CPU cycles.

        pygame.key.set_mods(0)      # don't ask me why this is needed, but without it, L_CTRL is pressed initially

    #----------------------------------------------------------------------
    def Run(self):

        print threading.currentThread()
        #raise NameError

        #pygame.time.set_timer(TIMEREVENT, timerspeed)
        self.keepGoing = 1

        while self.keepGoing:
            self.evManager.Post()

            for event in pygame.event.get():
                #ev = None
                if event.type == QUIT:
                    eV = QuitEvent()
                    #self.evManager.Post( eV )
                    queue.put(eV)

                #used = self.view.app.event(event)
                #if used != None:
                #   if used[1] == None:
                    #   self.view.view_refresh_needed = 1

#                if self.runninggame:
#                    self.subcontroller.HandlePyGameEvent(event)
                self.subcontroller.HandlePyGameEvent(event)
                    
            self.subcontroller.HandleTimerEvent()
            

            if self.runninggame:    #runninggame really means showing map
                #self.view.view_refresh_needed = 1
                if self.game.amihost:
                    if self.game.move_mode == 'free':
                        if not self.in_free_move_mode:
                            self.in_free_move_mode = True
                            self.my_clock = pygame.time.Clock()
                            self.time_since_last_game_update = 0
                        else:
                            self.time_since_last_game_update += self.my_clock.tick() 
                            if self.time_since_last_game_update >= self.free_move_update_interval:
                                game_time_advance = self.time_since_last_game_update * self.game_speed
                                self.time_since_last_game_update = 0
                                self.controller_handle_game_timed_events_in_free_move_mode(game_time_advance)
#                            self.game.set_time(self.game.Time + 0.1)
#                            self.timed_event_list.append(self.game.Time + 0.1, ['set time', self.game.Time + 0.1])
                    else:
                        if self.in_free_move_mode:
                            hgc.clear_free_move_orders(self.game)
                            self.in_free_move_mode = False

                eV = UpdateViewEvent()
                #self.evManager.Post( eV )
                queue.put(eV)

            else:
#                self.pguapp.screen.fill((0,150,0))
#                rects = self.pguapp.update()
                rects = self.pguapp.refresh()
#                print rects
                pygame.display.update(rects)
                
#                self.pguapp.paint()
#                pygame.display.update()


            pygame.time.wait(timerspeed)

        pygame.quit()

    #----------------------------------------------------------------------

    def OneFr(self):

        for event in pygame.event.get():
            ev = None
            if event.type == QUIT:
                eV = QuitEvent()
                #self.evManager.Post( eV )
                queue.put(eV)

            used = self.view.app.event(event)
            if used != None:
                if used[1] == None:
                    self.view.view_refresh_needed = 1

            if self.runninggame:
                self.subcontroller.HandlePyGameEvent(event)

        if self.runninggame:
            self.subcontroller.HandleTimerEvent()
            #self.view.view_refresh_needed = 1
            eV = UpdateViewEvent()
            #self.evManager.Post( eV )
            queue.put(eV)
        else:
            self.view.app.paint(self.view.window)
            pygame.display.update()

#    def twistrun(self):
#        self.OFR = task.LoopingCall(self.OneFr)
#        self.OFR.start(self.timerinterval)
#        reactor.run()

    #----------------------------------------------------------------------
    def SwitchController(self, key):

        if not self.guiClasses.has_key( key ):
            raise NotImplementedError
        self.subcontroller = self.guiClasses[key]
        
        
    def controller_handle_game_timed_events_in_free_move_mode(self, game_time_advance):
        self.game.saveandload.restoreSave('hostcomplete')
        del hctp_orddat[:]
        hctp_orddat.append([])
        global np
        np = 0
        orddat = hctp_orddat[0]
        next_time = self.game.Time + game_time_advance
#        print 'controllers, hgte', next_time, self.game.Time, game_time_advance
        hgc.generate_events_during_time_advance(next_time, self.game)
        
        orders_timed_event_list.sort(key=lambda entry: entry[1])
        effects_timed_event_list.sort(key=lambda entry: entry[1])
        other_timed_event_list.sort(key=lambda entry: entry[1])
        
        timed_events_occurring = []
        for timed_event_list in [orders_timed_event_list, effects_timed_event_list, other_timed_event_list]:

            timed_events_occurring.extend( hgc.find_timed_events_occurring(timed_event_list, next_time,0,'free') )
            
#            highest_idx = -1
#            for idx, event_entry in enumerate(timed_event_list):
#                if event_entry[0] <= next_time:
#                    timed_event = event_entry
#                    timed_events_occurring.append(timed_event)
#    #                hgc.handle_game_timed_event(timed_event)
#                    highest_idx = idx
#                else:
#                    break
#            timed_event_list[0:highest_idx+1] = []
            
        timed_events_occurring.sort(key=lambda entry: entry[0])    
#        timed_events_occurring.insert(0,(0,next_time,['game', 'set time', next_time]))        
        hgc.handle_game_timed_events(timed_events_occurring, self.game)
        
        self.game.set_time(next_time)
        ev = HostSendDataEvent('set time',next_time)
        queue.put(ev)
        ev = HostSendDataEvent('free_move_results',orddat)
        queue.put(ev)

        self.game.saveandload.restoreSave('player')
        

    def WaitForAll(self, event):
        print 'controllers, wait for all', self.amihost, self.finishedSoFar, event.code, self.myprofname, event.profname
        if self.amihost:     # every client that comes here on host computer appends
            self.finishedSoFar.append(event.profname)

        if self.amihost and event.profname == self.myprofname:   # the true host computer sets these values
            self.hostCheckedIn = 1
#            self.numclients = event.numclients
            self.code = event.code
            self.otherargs = event.otherargs
        elif not self.amihost:   # the clients, on client computer, send signal to come back to this function but on host comp
            eV = SendDoneSignal(self.myprofname)
            #self.evManager.Post( eV )
            queue.put(eV)
            # send signal to host that done creating

        if self.amihost and self.hostCheckedIn:
            
            if len(self.finishedSoFar) >= self.numclients:
                print 'controllers, wait for all2', self.finishedSoFar, self.code
            	self.finishedSoFar = []
            	self.hostCheckedIn = 0

                if self.code == 'Init Screen Done':
#                    rseed = random.randrange(0, sys.maxint)
#                    print 'TaDa!'
                    eV = HostSendDataEvent('initscreendone') 
                    queue.put(eV)
#                    eV = InitScreenDoneEvent()
#                    eV = MPChoicesDone_Host(rseed)
                elif self.code == 'Initial Create':
                    eV = AllInitUnitsCreated()
                    queue.put(eV)
                elif self.code == 'Orders Done':
                    eV = AllHumanOrdersSubmitted()
                    queue.put(eV)

            	#self.evManager.Post( eV )

    def switch_to_targeting_controller(self,event):
        self.choose_target_c.msg_window_ref = event.window_ref
        self.choose_target_c.cancel_func = event.cancel_func
        self.view.target_mode = True
        self.SwitchController( 'choose_target' )

    def switch_to_main_map_controller(self):
            self.view.target_mode = False
            self.SwitchController( 'mainmap' )
     
    def switch_to_modal_controller(self, event):
        self.modal_window_c.window_ref = event.window_ref
        self.SwitchController( 'modalwindow' )
             
    def hide_modal_window(self, event):
        self.pguctrl.hide_modal_window()
        if self.pguctrl.modal_windows_showing >= 1:
            self.view.modal_window_rect = self.pguctrl.modal_window_instances[-1].rect
            ev = SwitchToModalControllerEvent(self.pguctrl.modal_window_instances[-1])
            self.switch_to_modal_controller(ev)
        else:                        
            self.view.modal_window_rect = None
            self.switch_to_main_map_controller()
            
#        if self.pguctrl.secondary_modal_window_showing:
#            self.pguctrl.hide_secondary_modal_window()
#            self.view.modal_window_rect = self.pguctrl.modal_window_instance.rect
#            ev = SwitchToModalControllerEvent(self.pguctrl.modal_window_instance)
#            self.switch_to_modal_controller(ev)            
#        else:
#            self.pguctrl.hide_modal_window()
#            self.view.modal_window_rect = None
#            self.switch_to_main_map_controller()
            
    #----------------------------------------------------------------------
    def Notify(self, event):

        if isinstance( event, QuitEvent ):
            #this will stop the while loop from running
            if self.newmc == 0:
                self.keepGoing = False
            else:
                self.OFR.stop()
                reactor.stop()

#            pygame.quit()

        #elif isinstance( event, ChangeMCEvent ):
        elif isinstance( event, SPChoicesDone ):
            self.singleplayer = 1

            self.game = Game(self.evManager, self.ipsdata, self.singleplayer, self.amihost, self.myprofname)

            '''
            self.SwitchController( 'mainmap' )
            self.runninggame = 1
            self.pguctrl.StartGame()
            '''

        elif isinstance( event, InitScreenDoneEvent):
            # executed by all simultaneously, host and clients and singleplayer
#            self.singleplayer = 0
            self.game = Game(self.evManager, self.ipsdata, self.ismulti, self.amihost, self.myprofname)
            self.clientresults = ClientRoundResults(self.game, self.evManager, self.view)
        
            eV = LoadGraphicsEvent()
            queue.put(eV)
            if self.amihost:
                eV = UpdatePreTownScreenEvent()
#                eV = PrepareTownEvent()
                queue.put(eV)

        elif isinstance( event, SwitchToEncounterModeEvent):
            self.SwitchController( 'mainmap' )
            self.pguctrl.StartEncounter()
            self.my_clock = pygame.time.Clock()
            self.runninggame = 1
            
        elif isinstance( event, MPChoicesDone_Host):
            self.singleplayer = 0
            game = Game(self.evManager, self.ipsdata, self.singleplayer, self.amihost, self.myprofname, event.rseed)
            self.SwitchController( 'mainmap' )
            self.runninggame = 1
            self.pguctrl.StartGame()

        elif isinstance( event, MPChoicesDone_Client):
            self.singleplayer = 0
            game = Game(self.evManager, self.ipsdata, self.singleplayer, self.amihost, self.myprofname, event.rseed)
            self.SwitchController( 'mainmap' )
            self.runninggame = 1
            self.pguctrl.StartGame()

        elif isinstance( event, WaitForAllClients):
            self.WaitForAll(event)

        elif isinstance( event, SetHostAndProfAndIpsdata ):
            self.amihost = event.amihost
            self.myprofname = event.profname
            self.ipsdata = event.ipsdata
            self.ismulti = event.ismulti
            self.numclients = event.numclients

        elif isinstance( event, AllowOrders ):
            self.mainmapC.alloworders = 1
            self.pguctrl.tp.enableOrdersFinishedButton(True)

        elif isinstance( event, DisAllowOrders ):
            self.mainmapC.alloworders = 0
            self.pguctrl.tp.enableOrdersFinishedButton(False)

        elif isinstance( event, EnableDoneButton ):
            self.pguctrl.tp.enableOrdersFinishedButton(event.do_enable)

        elif isinstance( event, showSupplyPopUpEvent ):
            self.citysupplyPopupC.addingToRoute = True

        elif isinstance( event, hideSupplyPopUpEvent ):
            self.citysupplyPopupC.addingToRoute = False

        elif isinstance (event, SwitchToModalControllerEvent ):
            self.switch_to_modal_controller(event)
#            self.modal_window_c.window_rect = event.window_ref.rect

        elif isinstance (event, SwitchToMainMapControllerEvent ):
            self.switch_to_main_map_controller()

        elif isinstance( event, DragInModalEvent ):
            self.modal_window_c.drag_in_progress = event.drag
            
        elif isinstance( event, HideModalWindowEvent ):
            self.hide_modal_window(event)
            
        elif isinstance( event, SwitchToTargetingControllerEvent ):
            self.switch_to_targeting_controller(event)
#            oevent = event.first_event
#            self.choose_target_c.msg = event.msg
#            self.choose_target_c.source = oevent.source
#            self.choose_target_c.validate_func = oevent.validate_func
#            self.choose_target_c.chosen_func = oevent.chosen_func


            
