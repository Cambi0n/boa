#import wx
#import time
from events import *
from mobile_object import *
from internalconstants import *
from userconstants import *
#from math import fabs
from pgu import gui
import pguutils as pguu


class TopPanel(gui.Table):
    def __init__(self, pgua, view, **params):
        gui.Table.__init__(self, **params)
        self.pgua = pgua
        self.view = view
        
        self.butstyle2 = {}
        self.butstyle2['padding_left'] = 0
        self.butstyle2['padding_right'] = 0
        self.butstyle2['padding_top'] = 0
        self.butstyle2['padding_bottom'] = 0
        self.butstyle2['border_left'] = 0
        self.butstyle2['border_right'] = 0
        self.butstyle2['border_top'] = 0
        self.butstyle2['border_bottom'] = 0
        
        
        
        self.ofb = pguu.BmpButton(gui.Image(resourcepath + "donebtn.png"), theme = 'gui2theme', style = self.butstyle2)
        self.ofb.SetBmp(gui.Image(resourcepath + "donebtnhover.png"), 'hover')
        self.ofb.SetBmp(gui.Image(resourcepath + "donebtnhover.png"), 'down')
        
        self.ofb.connect(gui.CLICK, self.OnDone)
        
        self.mc = MovieControls(background = (140,140,140), theme = 'gui2theme')

        self.action_group = gui.Group()
#        self.standard_action_button = gui.Button("Standard")
#        self.standard_action_tool = gui.Tool(self.action_group, self.standard_action_button, value = 'standard')
        self.standard_action_tool = gui.Tool(self.action_group, gui.Label('Standard'), value = 'standard')
#        self.standard_action_button.connect(gui.CLICK, self.action_mode_change,'standard')
#        self.move_action_button = gui.Button("Move")
#        self.move_action_tool = gui.Tool(self.action_group, self.move_action_button, value = 'move')
        self.move_action_tool = gui.Tool(self.action_group, gui.Label('Move'), value = 'move')
#        self.move_action_button.connect(gui.CLICK, self.action_mode_change,'move')
        self.action_group.connect(gui.CHANGE, self.action_mode_change)
        
        self.td(self.standard_action_tool)
        self.td(self.move_action_tool)
#        self.td(self.standard_action_button)
#        self.td(self.move_action_button)

        
#         self.td(gui.Spacer(width = 20, height = 1))
        self.td(self.mc)
        self.td(gui.Spacer(width = 20, height = 1))
        self.td(self.ofb, align = 1)
        
    def OnDone(self):
        eV = OrdersDone()
        queue.put(eV)

    def enableOrdersFinishedButton(self,doenable):
        self.ofb.disabled = not doenable      
        self.ofb.repaint()  

    def action_mode_change(self):
        sp = self.view.selectedSprite
        if hasattr(sp,"object"):
            if isinstance(sp.object,MobileObject):
                ev = ChangeObjectsActionModeEvent(sp.object, self.action_group.value)
                queue.put(ev)

    def set_action_mode(self, new_mode):
        if new_mode == 'standard':
            self.standard_action_tool.click()
            self.standard_action_tool.pcls = 'down'
        elif new_mode == 'move':
            self.move_action_tool.click()
            self.move_action_tool.pcls = 'down'
        else:
            self.action_group.value = None
            self.standard_action_tool.pcls = ''
            self.move_action_tool.pcls = ''
        self.resize()
        self.repaint()


class MovieControls(gui.Table):
    def __init__(self, **params):
        gui.Table.__init__(self, **params)

        self.butstyle = {}
        self.butstyle['padding_left'] = 0
        self.butstyle['padding_right'] = 0
        self.butstyle['padding_top'] = 0
        self.butstyle['padding_bottom'] = 0
        self.butstyle['border_left'] = 0
        self.butstyle['border_right'] = 0
        self.butstyle['border_top'] = 0
        self.butstyle['border_bottom'] = 0
        bimg = gui.Image(resourcepath + "bluebackbtn6.png")
        self.butstyle['background','hover'] = bimg
        self.butstyle['background','down'] = bimg
        self.butstyle['width'] = bimg.style.width
        self.butstyle['height'] = bimg.style.height
        
        b = pguu.BmpButton(gui.Image(resourcepath + "bdf2left24.png"), theme = 'gui2theme', style = self.butstyle)
        b.connect(gui.CLICK, self.OnBackFullBtn)
        self.td(b)
        
        b = pguu.BmpButton(gui.Image(resourcepath + "bdfleftstep24.png"), theme = 'gui2theme', style = self.butstyle)
        b.connect(gui.CLICK, self.OnBackOneBtn)
        self.td(b)
        
        self.playimg = gui.Image(resourcepath + "bdf1right24.png")
        self.pauseimg = gui.Image(resourcepath + "bdfpause24.png")
        self.playpausebtn = pguu.BmpButton(self.playimg, theme = 'gui2theme', style = self.butstyle)
        self.playpausebtn.connect(gui.CLICK, self.OnPlayBtn)
        self.td(self.playpausebtn)

        b = pguu.BmpButton(gui.Image(resourcepath + "bdfrightstep24.png"), theme = 'gui2theme', style = self.butstyle)
        b.connect(gui.CLICK, self.OnForwardOneBtn)
        self.td(b)

        b = pguu.BmpButton(gui.Image(resourcepath + "bdf2right24.png"), theme = 'gui2theme', style = self.butstyle)
        b.connect(gui.CLICK, self.OnForwardFullBtn)
        self.td(b)

        if turn_mode == 'we_go_they_go':
            tot_num_pulses = 2*num_pulses_per_unit
        self.slider = gui.HSlider(value=0,min=0,max=tot_num_pulses,size=20,height=16,width=120)
        self.slider.connect(gui.CHANGE, self.OnSliderScrollThumbtrack)
        self.slider.connect(gui.MOUSEBUTTONDOWN, self.OnSliderScrollMouseDown)
        self.td(self.slider)
        
#        self.staticText = gui.Label('0', width = 200)
        self.staticText = pguu.LabelMinSpace('0', width = 40)
        self.td(self.staticText)

        self.lastFrameShown = 0

        self.movierunning = False
        
        self.disabled = True

    def OnBackFullBtn(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)
            
#        eV = ClearSelectionEvent()
#        queue.put(eV)
            
        ev = RunMovie(0, 0, False)
        queue.put(ev)

    def OnBackOneBtn(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)
#        eV = ClearSelectionEvent()
#        queue.put(eV)
        currentframe = self.slider.value
        if currentframe > 0:
            ev = RunMovie(currentframe - 1, 0, False)
            queue.put(ev)

    def OnPlayBtn(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)
        else:
#            eV = ClearSelectionEvent()
#            queue.put(eV)
            ev = RunMovie(self.max_frame_now, normalmovieframedelay)
            queue.put(ev)

    def OnForwardOneBtn(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)
#        eV = ClearSelectionEvent()
#        queue.put(eV)
        currentframe = self.slider.value
        if currentframe < self.max_frame_now:
            ev = RunMovie(currentframe + 1, 0)
            queue.put(ev)

    def OnForwardFullBtn(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)
#        eV = ClearSelectionEvent()
#        queue.put(eV)
        ev = RunMovie(int(self.max_frame_now),0, False)
        queue.put(ev)

    def OnSliderScrollMouseDown(self):
        if self.movierunning:
            ev = PauseMovie()
            queue.put(ev)

    def OnSliderScrollThumbtrack(self):
        if not self.movierunning and not self.updating:
            ttval = self.slider.value
            if ttval > self.max_frame_now:
                ttval = self.max_frame_now
            ev = RunMovie(ttval, 0, False, False)
            queue.put(ev)
        
    def updateMovieControls(self,movie,movierunning):
        if movierunning != self.movierunning:
            self.movierunning = movierunning
            if self.movierunning:
                self.playpausebtn.SetBmp(self.pauseimg, 'normal')
            else:
                self.playpausebtn.SetBmp(self.playimg, 'normal')
        
        self.staticText.value = str(int(movie.frame))
        self.updating = True
        self.slider.value = movie.frame
        self.updating = False
        self.lastFrameShown = movie.frame
        self.max_frame_now = movie.numframes
        self.resize()
        self.repaint()
        
    def enableMC(self):
        self.disabled = False
