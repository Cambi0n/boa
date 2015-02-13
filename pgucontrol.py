#import Queue
import pygame
from pygame.locals import MOUSEMOTION
from internalconstants import *
#from wxstartupgc import *
#from wxgamefuncs import *
#from wxorderfuncs import *
from pgu import gui
import toppanel as top
import trimmedlabels as tl
import townview as tview
import pguutils as pguu
import info_popup


class pguControl():

#    global queue
    def __init__(self, pguapp, evManager, wind):
        self.pguapp = pguapp
        self.evManager = evManager
        self.wind = wind
        self.c = gui.Container(x = 0, y = 0, width = wind.get_width(), height = wind.get_height(), background = (0,0,0,0))
        
        self.pfm_showing = False
        self.sfm_showing = False
#        self.modal_window_showing = False
#        self.secondary_modal_window_showing = False
#        self.modal_window_instance = None
#        self.secondary_modal_window_instance = None
        self.modal_windows_showing = 0       # when 0, no modal windows up.
        self.modal_window_instances = []
        self.nonmodal_popup_showing = False
        self.nonmodal_popup_instance = None        
        
#        self.townc = gui.Container(x = 0, y = 0, width = wind.get_width(), height = wind.get_height(), background = (20,20,80))

    def StartEncounter(self):
        self.c = gui.Container(x = 0, y = 0, width = self.wind.get_width(), height = self.wind.get_height(), background = (0,0,0,0))
        self.pguapp.init(self.c)
        self.c.add(self.tp, 0, 0)
        self.tp.resize()
        self.tp.repaint()
        self.view.view_refresh_needed = True
        
    def CreatePanels(self, view):
#        FirstScreen(self, -1, evManager)
        self.view = view
        
        self.tlab = tl.trimAllLabels(view)
        
        self.tp = top.TopPanel(self.pguapp, self.view, width = self.wind.get_width(), height = toppanel_height, 
                               background = (20,20,100), theme = 'gui2theme')      
    
        self.tscr = tview.TownView(self, background = (20,20,80))
        self.ptscr = tview.PreTownView(self, background = (20,20,80))
    
    def ShowTownScreen(self):
        self.pguapp.init(self.tscr)
        
    def show_pre_town_screen(self):
        self.pguapp.init(self.ptscr)
        
    def UpdateMovieControls(self,movie, movierunning):
        self.tp.mc.updateMovieControls(movie, movierunning)
#        self.view.view_refresh_needed = True

    def ShowTopPanel(self):
        pass
#        self.tp.Show()
#        self.SetFocusIgnoringChildren()
#        print 'focus after showing toppanel', self.FindFocus(), threading.currentThread()


    def HideTopPanel(self):
        pass
#        self.tp.Hide()

    def set_toppanel_action_mode(self, object, new_action_mode = None):
        if object:
            if not new_action_mode:
                new_action_mode = object.action_mode
        self.tp.set_action_mode(new_action_mode)
       
    def create_primary_floating_menu(self, data, pos_info, background = (0,0,0,180)):
        self.pfm = pguu.FloatingMenu(data, pos_info, background = background)
        if not self.pfm_showing:
            print 'pguu, create pfm', self.pfm
            self.c.add(self.pfm, self.pfm.rect.x, self.pfm.rect.y)
            self.pfm_showing = True
        self.pfm.resize()
        self.pfm.repaint()
        self.view.view_refresh_needed = True
        return self.pfm
        
    def hide_primary_floating_menu(self):
        if self.pfm_showing:
            self.pfm_showing = False
            print 'pguu, hide pfm', self.pfm
            self.c.remove(self.pfm)
            self.pguapp.resize()
            self.view.view_refresh_needed = True
            
    def create_secondary_floating_menu(self, data, pos_info):
        self.sfm = pguu.FloatingMenu(data, pos_info, background = (0,0,180,100))
        if not self.sfm_showing:
            self.c.add(self.sfm, self.sfm.rect.x, self.sfm.rect.y)
            self.sfm_showing = True
        self.sfm.resize()
        self.sfm.repaint()
        self.view.view_refresh_needed = True
        return self.sfm
        
    def hide_secondary_floating_menu(self):
        if self.sfm_showing:
            self.sfm_showing = False
            self.c.remove(self.sfm)
            self.pguapp.resize()
            self.view.view_refresh_needed = True
            
    def show_modal_window(self, modal_window, topleft):
#        self.info_popup_instance = info_popup.InfoPopup(data)
        self.modal_windows_showing += 1
        self.modal_window_instances.append(modal_window)
        self.c.add(modal_window, topleft[0], topleft[1])
        if self.modal_windows_showing == 1:
            oldtop = False
        else:
            if hasattr(self.modal_window_instances[self.modal_windows_showing-2],'mouse_motion_outside'):
                oldtop = True
            else:
                oldtop = False
        if hasattr(modal_window,'mouse_motion_outside'):
            newtop = True
        else:
            newtop = False
#        if not justone and hasattr(self.modal_window_instances[self.modal_windows_showing-2],'mouse_motion_outside'):
#            oldtop = True
#        else:
#            oldtop = False
        if newtop and not oldtop: 
            self.c.connect(MOUSEMOTION, self.motion_outside_modal)
        elif not newtop and oldtop:
            self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
            
            
#        if hasattr(modal_window,'mouse_motion_outside'):
#            self.c.connect(MOUSEMOTION, self.motion_outside_modal)
#        elif self.modal_windows_showing >= 2 and hasattr(self.modal_window_instances[self.modal_windows_showing-1],'mouse_motion_outside'):
#            self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
            
        modal_window.resize()
        modal_window.repaint()
        self.view.view_refresh_needed = True
#        return self.info_popup_instance

    def show_modal_window_old(self, modal_window, topleft):
#        self.info_popup_instance = info_popup.InfoPopup(data)
        print 'pguctrl, show modal window', self.modal_window_instance
        self.modal_window_instance = modal_window
        print 'pguctrl, show modal window2', self.modal_window_instance
        if not self.modal_window_showing:
            self.c.add(self.modal_window_instance, topleft[0], topleft[1])
            self.modal_window_showing = True
            if hasattr(self.modal_window_instance,'mouse_motion_outside'):
                self.c.connect(MOUSEMOTION, self.motion_outside_modal)
            
        self.modal_window_instance.resize()
        self.modal_window_instance.repaint()
        self.view.view_refresh_needed = True
#        return self.info_popup_instance
        
    def hide_modal_window(self):
        if self.modal_windows_showing > 0:
            self.modal_windows_showing -= 1
            oldtopwind = self.modal_window_instances[-1]
            self.c.remove(oldtopwind)

            if self.modal_windows_showing == 0:
                newtop = False
            else:
                newtopwind = self.modal_window_instances[-2]
                if hasattr(newtopwind,'mouse_motion_outside'):
                    newtop = True
                else:
                    newtop = False
            if hasattr(oldtopwind,'mouse_motion_outside'):
                oldtop = True
            else:
                oldtop = False
            if newtop and not oldtop: 
                self.c.connect(MOUSEMOTION, self.motion_outside_modal)
            elif not newtop and oldtop:
                self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
            
#            if hasattr(self.modal_window_instances[-1],'mouse_motion_outside'):
#                if self.modal_windows_showing == 0 or not hasattr(self.modal_window_instances[self.modal_windows_showing],'mouse_motion_outside'):
#                    self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
#            elif self.modal_windows_showing != 0 and hasattr(self.modal_window_instances[self.modal_windows_showing],'mouse_motion_outside'):
#                self.c.connect(MOUSEMOTION, self.motion_outside_modal)
                    
            self.modal_window_instances.pop()
            self.pguapp.resize()
            self.view.view_refresh_needed = True
        
    def hide_modal_window_old(self):
        if self.modal_window_showing:
            self.modal_window_showing = False
            self.c.remove(self.modal_window_instance)
            if hasattr(self.modal_window_instance,'mouse_motion_outside'):
                self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
            self.pguapp.resize()
            self.view.view_refresh_needed = True
        
    def show_secondary_modal_window(self, modal_window, topleft):
#        self.info_popup_instance = info_popup.InfoPopup(data)
        self.secondary_modal_window_instance = modal_window
        if not self.secondary_modal_window_showing:
            self.c.add(self.secondary_modal_window_instance, topleft[0], topleft[1])
            self.secondary_modal_window_showing = True
            if hasattr(self.secondary_modal_window_instance,'mouse_motion_outside'):
                self.c.connect(MOUSEMOTION, self.motion_outside_modal)
            
        self.secondary_modal_window_instance.resize()
        self.secondary_modal_window_instance.repaint()
        self.view.view_refresh_needed = True
#        return self.info_popup_instance
        
    def hide_secondary_modal_window(self):
        if self.secondary_modal_window_showing:
            self.secondary_modal_window_showing = False
            self.c.remove(self.secondary_modal_window_instance)
            if hasattr(self.secondary_modal_window_instance,'mouse_motion_outside'):
                self.c.disconnect(MOUSEMOTION, self.motion_outside_modal)
            self.pguapp.resize()
            self.view.view_refresh_needed = True
        
    def motion_outside_modal(self,_event):
        # sometimes mouse moves outside modal window, and something
        # needs to happen when that does, but the window won't receive
        # any events any more because it's modal
        if self.modal_window_instances != []:
            top_modal_window = self.modal_window_instances[-1]
            if not top_modal_window.rect.collidepoint(_event.pos):
                top_modal_window.mouse_motion_outside()
            
#        if self.secondary_modal_window_showing:
#            if not self.secondary_modal_window_instance.rect.collidepoint(_event.pos):
#                self.secondary_modal_window_instance.mouse_motion_outside()
#            
#        elif self.modal_window_showing:
#            if not self.modal_window_instance.rect.collidepoint(_event.pos):
#                self.modal_window_instance.mouse_motion_outside()
                
    def show_nonmodal_popup(self, nonmodal_popup, topleft):
        self.nonmodal_popup_instance = nonmodal_popup
        if not self.nonmodal_popup_showing:
            self.c.add(self.nonmodal_popup_instance, topleft[0], topleft[1])
            self.nonmodal_popup_showing = True
            
        self.nonmodal_popup_instance.resize()
        self.nonmodal_popup_instance.repaint()
        self.view.view_refresh_needed = True

    def hide_nonmodal_popup(self):
        if self.nonmodal_popup_showing:
            self.nonmodal_popup_showing = False
            self.c.remove(self.nonmodal_popup_instance)
            self.pguapp.resize()
            self.view.view_refresh_needed = True
        

    def add_timed_message(self,surf,x,y,duration = 3000):
        pguu.TimedImage(surf,self.c,x,y,self.func_after_adding, self.func_after_removing,stay_time = duration)
        
    def func_after_adding(self):
        self.view.view_refresh_needed = True
    def func_after_removing(self):
        self.pguapp.resize()
        self.view.view_refresh_needed = True
        
