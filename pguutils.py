import threading
import os
import pygame
from pgu import gui
from internalconstants import *

#import gcutils
#from gui.const import *


class BmpButton(gui.Button):
    """A button, buttons can be clicked, they are usually used to set up callbacks.
    
    Example:
        w = gui.Button("Click Me")
        w.connect(gui.CLICK, fnc, value)

    """

    def __init__(self, value=None, **params):
        """Bitmap Button constructor, which takes either a string label or widget.
        
        Intention of this class is for value to be a gui.Image
        
        uses a new self.cls (necessary for themes) and can use different
        bitmaps for different states (self.pcls) such as hovering or pressed
        
        See Widget documentation for additional style parameters.

        """
        params.setdefault('cls', 'bmpbutton')
        if value == None:
            tempsurf = pygame.Surface( (16,16) )
            tempsurf = tempsurf.convert_alpha()
            tempsurf.fill((0,0,0,128)) #make semi-transparent surface
            value = gui.Image(tempsurf)
            
        gui.Button.__init__(self, value, **params)
        
        self._bitmaps = {"normal": self.value, "disabled": None,
                         "hover": None, "down": None}
        self.customDisabled = False        


    def SetBmp(self, img, status):
        ''' img should be either a file name or a pygame surface
        
            Since the bounding rectangle doesn't change with a different bitmap,
            it's probably best to keep each bitmap the same size --bdf
        '''
        
#        bmp = gui.Image(img)
        self._bitmaps[status] = img
        if status == 'disabled':
            self.customDisabled = True
    
    def paint(self,s):
        ''' I thought about having self.value change when self.pcls changes,
        but the disabled state isn't a pcls.  
        '''
        
        w = None
        if self.customDisabled:
            if self._bitmaps['disabled']:
                w = self._bitmaps['disabled']
            else:
                self.customDisabled = False
        if not w:
            if self.pcls == 'hover' and self._bitmaps['hover']:
                w = self._bitmaps['hover']
            elif self.pcls == 'down' and self._bitmaps['down']:
                w = self._bitmaps['down']
            else:
                w = self._bitmaps['normal']  
                
#        if w != self.value:
#            self.value = w
#            self.resize()
                
        w.pcls = self.pcls
#        w.paint(gui.surface.subsurface(s,self._rect_border))
        w.paint(gui.surface.subsurface(s,self.value.rect))
        
#        self.value.pcls = self.pcls
#        self.value.paint(gui.surface.subsurface(s,self._rect_border))


class PersistentHoverCont(gui.Container):
    """A container meant to be used in a group of containers.  
    The container that last received the hover retains a hover appearance
    until another container in the group gets hover
    
    Example:
        g = gui.Group(value=1)
        
        t = gui.Table()
        t.tr()
        t.td(gui.PersistentHoverCont(g, 1))
        t.tr()
        t.td(gui.PersistentHoverCont(g, 2))
        t.tr()
        t.td(gui.PersistentHoverCont(g, 3))

    """
    

    def __init__(self, group, value=None, **params):

        """
        Keyword arguments:    
            group -- a gui.Group for the Tool to belong to
            widget -- a widget to appear on the Tool (similar to a Button)
            value -- the value

        """
        
        params.setdefault('cls','persistenthovercont')
        gui.Container.__init__(self,**params)
        self.group = group
        self.group.add(self)
        self.value = value
        
        if self.group.value == self.value: self.pcls = "hover"

        self.connect(gui.ENTER, self.onenter)
        self.connect(gui.EXIT, self.onexit)

    def onenter(self):
        for w in self.group.widgets:
            if w != self: 
                w.pcls = ""
#                w.repaint
        self.group.value = self.value

    def onexit(self):
        self.pcls = "hover"
        self.repaint()


    
class FocusCont(gui.Container):
    """A container meant to be used in a group of containers.
    The container in the group with focus receives a pcls of 'focus'.
      
    Example:
        g = gui.Group(value=1)
        
        t = gui.Table()
        t.tr()
        t.td(gui.FocusCont(g, 1))
        t.tr()
        t.td(gui.FocusCont(g, 2))
        t.tr()
        t.td(gui.FocusCont(g, 3))

    """
    

    def __init__(self, group, value=None, **params):

        """
        Keyword arguments:    
            group -- a gui.Group for the Tool to belong to
            value -- the value

        """
        
        params.setdefault('cls','focuscont')
        gui.Container.__init__(self,**params)
        self.group = group
        self.group.add(self)
        self.value = value
        
        if self.group.value == self.value: self.pcls = "focus"

        self.connect(gui.FOCUS, self.onfocus)
#        self.connect(gui.BLUR, self.onblur)
        self.connect(gui.ENTER, self.onenter)
        self.connect(gui.EXIT, self.onexit)

    def onfocus(self):
        ''' after container focus event, will come here with this widget 'hover'
        and other widgets will be either 'focus' or '' '''
        
        self.group.value = self.value
        self.pcls = 'focushover'
        
        for w in self.group.widgets:
            if w != self:
                w.pcls = '' 
#                if w.pcls == "focushover":
#                    w.pcls = "hover"
#                elif w.pcls == "focus":
#                    w.pcls = ""
##                w.repaint
#        if self.pcls == 'hover':
#            self.pcls = 'focushover'
#        else:
#            self.pcls = 'focus'
            

    def onblur(self):
        if self.pcls == 'focushover':
            self.pcls = "hover"
        else:
            self.pcls = ""
        self.repaint()

    def onenter(self):
        ''' after container enter event, will come here with this widget 'hover'
        and other widgets '' '''
        if self.value == self.group.value:
            self.pcls = 'focushover'
        for w in self.group.widgets:
            if w != self: 
                if w.value == self.group.value:
                    w.pcls = 'focus'
#                w.repaint
#        self.group.value = self.value

    def onexit(self):
        if self.value == self.group.value:
            self.pcls = 'focus'
            
#        if self.pcls == 'focushover':
#            self.pcls = "focus"
        self.repaint()




#    def focus(self,w=None):
#        widget.Widget.focus(self) ### by Gal koren
##        if not w:
##            return widget.Widget.focus(self)
#        if not w: return
##       rearrange self.widgets so that widget that 
##       just received focus is on "top" --bdf        
#        if w in self.widgets:
#            topwidx = self.widgets.index(w)
#            self.widgets.pop(topwidx)
#            self.widgets.append(w)
#        if self.myfocus: self.blur(self.myfocus)
#        if self.myhover is not w: self.enter(w)
#        if w.focusable:
##        if True:
#            self.myfocus = w
#            w._event(pygame.event.Event(FOCUS))
#        
#        #print self.myfocus,self.myfocus.__class__.__name__
#    
#    def blur(self,w=None):
#        if not w:
#            return widget.Widget.blur(self)
#        if self.myfocus is w:
#            if self.myhover is w: self.exit(w)
#            self.myfocus = None
#            w._event(pygame.event.Event(BLUR))
#    
#    def enter(self,w):
#        if w.disabled: return
#        if self.myhover: self.exit(self.myhover)
#        self.myhover = w
#        w.pcls = 'hover'    # so container can get decorated on hover --bdf
#        w.repaint()
#        w._event(pygame.event.Event(ENTER))
#    
#    def exit(self,w):
#        if w.disabled: return
#        if self.myhover and self.myhover is w:
#            self.myhover = None
#            w.pcls = "" # so container can get decorated on hover --bdf
#            w.repaint()
#            w._event(pygame.event.Event(EXIT))    
#



class HoverScrollList(gui.Table):
    """A vertically scrollable area where hovering over a button at top and bottom causes scrolling ."""

    def __init__(self, widget, width=0, height=0, maxheight = 100, step=8, **params):
        """ScrollArea constructor.

        Arguments:
            widget -- widget to be able to scroll around
            width, height -- size of scrollable area.  Set either to 0 to default to size of widget.
            maxheight -- maximum vertical height of scrollable area.  
            step -- set to how far clicks on the icons will step 

        """
        w = widget
        params.setdefault('cls', 'hoverscrolllist')
        gui.Table.__init__(self, width=width,height=height,**params)
        
        self.sbox = gui.SlideBox(w, width=width, height=height, cls=self.cls+".content")
        self.widget = w
        self.topbutton = BmpButton(gui.Image(resourcepath + '1downarrow.png'))
        self.bottombutton = BmpButton(gui.Image(resourcepath + '1uparrow.png'))
        self.maxheight = maxheight
        self.step = step
        self.clock = pygame.time.Clock()
        self.timesince = 0
        
        print 'hoverscrolllist', self.widgets
    
    def __setattr__(self,k,v):
        if k == 'widget':
            self.sbox.widget = v
        self.__dict__[k] = v

    def resize(self,width=None,height=None):
        
        '''I am a table (call me hsl) that contains a topbutton (possibly), a slidebox, 
        then a bottombutton (possibly).  The slidebox is a container.  It contains only a table, 
        and this table is also called its widget.  Call this table widgettable.  widgettable 
        is also the widget of me (hsl)'''
        
        widget = self.widget
        box = self.sbox

        gui.Table.clear(self)
        
        widget.rect.w, widget.rect.h = widget.resize()
#        print widget.rect

#        if self.maxheight == 0:
#            self.maxheight = self.container.rect.h
#        else:
#            self.maxheight = min(self.container.rect.h,self.maxheight)
        
        my_width,my_height = self.style.width,self.style.height
        if not my_width:
            my_width = widget.rect.w
        if not my_height:
            my_height = min(widget.rect.h, self.maxheight)
            
            
        if widget.rect.h > self.maxheight:
            needbuttons = True
            tb = self.topbutton
            tb.rect.w,tb.rect.h = tb.resize()
            bb = self.bottombutton
            bb.rect.w,bb.rect.h = bb.resize()
            button_height = tb.rect.h + bb.rect.h
        else:
            needbuttons = False
            button_height = 0
            
        xt,xr,xb,xl  = gui.pguglobals.themes[self.style.theme].getspacing(box)
        box.style.width,box.style.height = my_width,my_height-(button_height+xt+xb)
        box.rect.w,box.rect.h = box.resize()

        if needbuttons:
#            self.topbutton = gui.Button("UP", width = my_width)
#            self.topbutton.resize(height = 32)
            self.tr() 
            self.td(tb)
#            tb.connect(gui.CLICK, self._scroll_changed, -1)
            tb.connect(gui.ENTER, self._start_scroll, -1)
            tb.connect(gui.EXIT, self._end_scroll)
#            tb.connect(gui.HOVER, self._scroll_changed, -1)
#            tb.connect(gui.ENTER, self._scroll_changed, -1)
        
        self.tr()
        self.td(box)
        
        if needbuttons:
#            self.bottombutton = gui.Button("DOWN", width = my_width)
            self.tr() 
            self.td(bb)
#            bb.connect(gui.CLICK, self._scroll_changed, 1)
            bb.connect(gui.ENTER, self._start_scroll, 1)
            bb.connect(gui.EXIT, self._end_scroll)
#            bb.connect(gui.HOVER, self._scroll_changed, 1)
#            bb.connect(gui.ENTER, self._scroll_changed, 1)
            
            self._set_button_state()     # to disable if necessary
            
        r = gui.Table.resize(self,width,height)
        return r
    
    def _start_scroll(self, dir):
#        self.r = gcutils.RepeatTimer(0.1, self._scroll_changed, args = [dir])
#        self.r = gcutils.RepeatTimer(0.05, self.hello,args = [1])
#        self.r.start()
#        pygame.time.set_timer(gui.HOVER, 50)
        self.dir = dir
        self.timerfunc = self._scroll_changed
#        self.addtimerfunc(self._scroll_changed)
        
    def _end_scroll(self):
#        self.r.cancel()
#        pygame.time.set_timer(gui.HOVER,0)
        self.timerfunc = None
    

#    def hello(self, num):
#        print 'hello', num

    def _sendEnter(self, w):
        if w.is_hovering():
            w._event(pygame.event.Event(gui.ENTER))
    
    def _scroll_changed(self):
        #y = (self.widget.rect.h - self.sbox.rect.h) * self.vscrollbar.value / 1000
        #if y >= 0: self.sbox.offset[1] = -y
        
#        if _widget:
#            t = threading.Timer(2, self._sendEnter, args = [_widget])
#            t.start()
#        pygame.time.wait(100)
#        self._sendEnter(_widget)
        
        self.timesince += self.clock.tick()
        if self.timesince > 25 and self.is_hovering():
#            print self.timesince
            self.timesince = 0
            sugg_offset = self.sbox.offset[1] + self.dir * self.step
            if sugg_offset < 0:
                sugg_offset = 0
            elif sugg_offset > self.sbox.max_rect.h - self.sbox.rect.h:
                sugg_offset = self.sbox.max_rect.h - self.sbox.rect.h
                
            self.sbox.offset[1] = sugg_offset
            
            self._set_button_state()
            self.sbox.reupdate()
#            self.reupdate()
                
    def _set_button_state(self):
                 
        if self.sbox.offset[1] <= 0:
            self.topbutton.container.exit(self.topbutton)
            self.topbutton.disabled = True
            self.timerfunc = None
        else:
            self.topbutton.disabled = False
        if self.sbox.offset[1] >= self.sbox.max_rect.h - self.sbox.rect.h:
            self.bottombutton.container.exit(self.bottombutton)
            self.bottombutton.disabled = True
            self.timerfunc = None
        else:
            self.bottombutton.disabled = False
            
        self.topbutton.repaint()
        self.bottombutton.repaint()

    def event(self, e):
         #checking for event recipient
         if (gui.Table.event(self, e)):
             return True

        
class LabelMinSpace(gui.Label):
    ''' a label class that with a min width and height
    equal to the width and height parameters passed in
    Note that this width and height are the size of the _rect_border
    so that the hover and focus box will be of the specified size.
    I don't know of an elegant way to do this... --bdf'''
    
    def __init__(self, value="", width = 1, height = 1, **params):
        params.setdefault('focusable', False)
        params.setdefault('cls', 'label')
        gui.Label.__init__(self, value = value, **params)

        ''' self.style.align is reset somewhere between here and self.paint, but
        I sure can't find where.  So just save it here. --bdf'''
        self.halign = self.style.align
        self.vertalign = self.style.valign

        self.setwidth = width
        self.setheight = height
        self.resize()
    
    def paint(self,s):
        """Renders the label onto the given surface."""
        
        sz = s.get_size()
        dx = sz[0] - self.fs[0]
        dy = sz[1] - self.fs[1]
        x = (self.halign+1)*dx/2
        y = (self.vertalign+1)*dy/2
        
        s1 = pygame.Surface(sz).convert_alpha()
        s1.fill((0,0,0,0))
        s1.blit(self.font.render(self.value, 1, self.style.color),(0,0))
        s.blit(s1,(x,y))
    
    def resize(self,width=None,height=None):
        # Calculate the size of the rendered text
        self.lrbord = self.style.padding_left + self.style.padding_right + self.style.border_left + self.style.border_right
        self.tbbord = self.style.padding_top + self.style.padding_bottom + self.style.border_top + self.style.border_bottom
        self.fs = self.font.size(self.value)
        self.style.width = max(self.setwidth-self.lrbord, self.fs[0])
        self.style.height = max(self.setheight-self.tbbord, self.fs[1])
        (self.rect.w, self.rect.h) =  (self.style.width, self.style.height)
        return (self.style.width, self.style.height)
        

class FloatingMenu(gui.Table):
    """A menu, usually brought up by a right click, that allows choices by a left click, or expands
    into a submenu when an expandable choice is hovered over.  The menu will appear in a location 
    such that the mouse (without moving from the location where the right click occurred) will be 
    positioned at one of the corners of this menu.  The pos_info parameter is a tuple containing
    (viewport click position, rect within which menu must stay, optional rect that must be avoided).  
    The second rect is used for submenus, so this second rect specifies the rect of the primary menu.
    There shalt be no submenus of submenus.  A background parameter may be passed to this 
    (background = ..., it will show up in **params). 
    
    Each menu item is a gui.BmpButton.  Almost anything can be specified as the widget for the button.
    Usually it will be a gui.Label or a gui.Image, but it can also be a container and many things can 
    be put into this container, such as an image and a label.  
    
    The data parameter is a dictionary that is rather extensive and precise.  
    
    In the specification below, there is generally a choice between 'string' or 'contents'.  These are 
    mutually exclusive.  If there is an entry for 'string', then this string is turned into a gui.Label.  
    Also if there is a 'string' entry, then there might also be entries for 'font' and 'color' which can 
    be used to override defaults if desired.  If there is a 'contents' entry, then the gui element must 
    be completely created and passed in as the value for 'contents' (e.g. a gui.Image, or a container
    with multiple elements).  If there is a 'contents' entry and the value of 'contents' is a gui.Image, 
    then there also might be an 'extra_bmps' entry which contains a dictionary of button images.  Allowed 
    keys for 'extra_bmps' are 'hover', 'down', and 'disabled', and the values should be gui.Image.  Another
    options if 'contents' is gui.Image is 'but_theme', to override default theme. 
    
    data['default']
    data['default']['font']     default font to be used for gui.Label for menu items 
    data['default']['color']    default color to be used for foreground of text of gui.Label
    data['default']['style']    default style for menu items (gui.BmpButtons)
    data['default']['theme']    default theme for menu items (gui.BmpButtons) (not used atm)
    
    data['title']        optional title for menu, a gui.Label
    data['title']['string']    string of the title
    data['title']['font']
    data['title']['color']
    data['title']['contents']    bmp or other gui element.  Since not a button, no possibility to
                                 need 'xtrabmps' option
    
    data['section']['divider']    optional line between sections of menu
    data['section']['divider']['width']    width of line
    data['section']['divider']['color']    color of line
    
    data['section'][1]    1st (and possibly only) section of menu items
    data['section'][1][1]    1st menu item of this section
    data['section'][1][1]['style']    will be used regardless of content (widget) of button
                                      it contains things like background color or image for button (often
                                      (0,0,0,0), background color or image of button when hovering,
                                      or pressed, border size of button (line around button), border
                                      color of button, border color when hovering or pressed, etc.
    data['section'][1][1]['string']  see above
    data['section'][1][1]['font']    
    data['section'][1][1]['color']   
    data['section'][1][1]['contents']    See above
    data['section'][1][1]['extra_bmps']    
    data['section'][1][1]['but_style']    (not used atm)
    data['section'][1][1]['but_theme']
    data['section'][1][1]['function']    a reference to the function to be called when 
                                         menu item (button) is pressed.  If 'function' is not
                                         present, then 'start_hover_function' will be present
                                         and 'end_hover_function' will be present.
    data['section'][1][1]['function_args']    a tuple or list of arguments to pass to function
    
    data['section'][1][1]['submenu_function']    function called when start hovering over this
                                                menu item, usually to bring up a sub-menu.
                                                If start_hover_function and end_hover_function aren't
                                                present, then 'function' key must be present.
                                                This function must take 2 arguments: 1st is boolean, 
                                                where True raises the submenu and False closes it;
                                                2nd is y pos of primary menu item that called this
                                                submenu
    data['section'][1][1]['end_hover_function']    function called when ending hovering over this
                                                menu item, usually to remove submenu, not used atm
    
    
    data['section'][1][2]    2nd menu item
    
    .
    .
    .
    data['section'][2]    2nd section
    data['section'][2][1]    1st menu item of 2nd section
    .
    .
    .
    
    """

    def __init__(self, data, pos_info, **params):
        params.setdefault('cls', 'floatingmenu')
        gui.Table.__init__(self, **params)
        
        self.data = data
        self.pos_info = pos_info
        self.menu_item_list = []
        self.string_menu_items = []
        
        if len(self.pos_info) == 3:
            self.is_submenu = True
        else:
            self.is_submenu = False
            self.menu_item_type = {}
            self.menu_item_ypos = {}
            
        self.submenu_up = False
        self.submenu_for = 0    # index of self.menu_item_list for which submenu is up  
        self.submenu_dict = {}  # associates primary menu items (keys) with submenu functions (values)  
        
        
        self.left_margin = 10
        if 'default' in data:
            data_def = data['default']
            if 'font' in data_def:
                self.def_font = data_def['font']
            if 'color' in data_def:
                self.def_color = data_def['color']
            if 'style' in data_def:
                self.def_style = data_def['style']
#            if 'theme' in data_def:
#                self.def_theme = data_def['theme']
                
        if not hasattr(self, 'def_font'):
            self.def_font = pygame.font.Font(None,12) 
        if not hasattr(self, 'def_color'):
            self.def_color = (255,255,255,255) 
        if not hasattr(self, 'def_style'):
            self.def_style = {  'padding_left':0, \
                                'padding_right':0, \
                                'padding_top':0, \
                                'padding_bottom':0, \
                                'border_left':0, \
                                'border_right':0, \
                                'border_top':0, \
                                'border_bottom':0, \
                                'background':(0,0,0,0), \
                                ('background','hover'):(255,255,255,50), \
                                ('background','down'):(255,255,255,100), \
                                ('border_color','hover'):(0,0,0,0), \
                                ('border_color','down'):(0,0,0,0) \
                              }
#        if not hasattr(self, 'def_theme'):
#            self.def_theme = default_theme 

        data_sec = data['section']
        
        self.dividers = False
        if 'divider' in data_sec:
            self.dividers = True
            self.divider_lines = []
            data_div = data['section']['divider']
            if 'width' in data_div:
                self.div_width = data_div['width']
            else:
                self.div_width = 1
            if 'color' in data_div:
                self.div_color = data_div['color']
            else:
                self.div_color = (255,255,255,255)
        
        
        if 'title' in data:
            data_title = data['title']
            if 'string' in data_title:
                self.td(gui.Spacer(width = 1, height = 6))
                self.tr()
                if 'font' in data_title:
                    tfont = data_title['font']
                else:
                    tfont = self.def_font
                if 'color' in data_title:
                    tcolor = data_title['color']
                else:
                    tcolor = self.def_color
                self.td(gui.Label(data_title['string'], font = tfont, color = tcolor))
                self.tr()
                self.td(gui.Spacer(width = 1, height = 6))
                self.tr()
                if self.dividers:
                    div_line = gui.Color(self.div_color,width=1,height=self.div_width) # change to full width after know full width
                    self.divider_lines.append(div_line)
                    self.td(div_line)  
                    self.tr()
                    
        data_sec = data['section']
        
        for idx in range(1,len(data_sec)+1):
            if idx in data_sec:
                this_sec = data_sec[idx]
                for midx in range(1,len(this_sec)+1):
                    if midx in this_sec:
                        menu_item = this_sec[midx]
                        if 'style' in menu_item:
                            this_style = menu_item['style']
                        else:
                            this_style = self.def_style
                            
#                        this_func = menu_item['function']
                        
                        if 'contents' in menu_item:
                            w = menu_item['contents']
                            
#                            if 'but_style' in menu_item:
#                                this_style = menu_item['but_style']
#                            else:
#                                this_style = {  'padding_left':0, \
#                                                'padding_right':0, \
#                                                'padding_top':0, \
#                                                'padding_bottom':0, \
#                                                'border_left':0, \
#                                                'border_right':0, \
#                                                'border_top':0, \
#                                                'border_bottom':0 \
#                                             }
                            if 'but_theme' in menu_item:
                                this_theme = menu_item['but_theme']
                            else:
                                this_theme = default_theme
                                    
                            this_item = BmpButton(w, theme = this_theme, style = this_style)
                                
                            if isinstance(menu_item['contents'], gui.Image):
                                if 'extra_bmps' in menu_item:
                                    for button_state, the_image in menu_item['extra_bmps'].iteritems():
                                        this_item.SetBmp(the_image, button_state)
                                        
                        elif 'string' in menu_item:
                            if 'font' in menu_item:
                                this_font = menu_item['font']
                            else:
                                this_font = self.def_font
                            if 'color' in menu_item:
                                this_color = menu_item['color']
                            else:
                                this_color = self.def_color
                            w = LabelMinSpace(menu_item['string'], font = this_font, color = this_color)
                            this_item = BmpButton(w, style = this_style)
                            self.string_menu_items.append(this_item)
                        else:
                            this_item = None
                            
                        if this_item:
                            self.td(this_item)
                            self.menu_item_list.append(this_item)
                            if 'function' in menu_item:
                                if 'function_args' in menu_item:
                                    f_args = menu_item['function_args']
                                else:
                                    f_args = []
                                this_item.connect(gui.CLICK, self.fm_function_callback, menu_item['function'], f_args)
                                if not self.is_submenu:
                                    this_item.connect(gui.ENTER, self.check_hover)
                                    self.menu_item_type[len(self.menu_item_list)-1] = 'function'
                            elif 'submenu_function' in menu_item:
                                if not self.is_submenu:
                                    self.menu_item_type[len(self.menu_item_list)-1] = 'submenu_function'
                                    self.submenu_dict[this_item] = menu_item['submenu_function']

                            else:
                                self.menu_item_type[len(self.menu_item_list)-1] = 'just_string'
                                
#                            if 'end_hover_function' in menu_item:
#                                this_item.connect(gui.EXIT, menu_item['end_hover_function'])
                            self.tr()
                
                if self.dividers and idx+1 in data_sec:
                    div_line = gui.Color(self.div_color,width=1,height=self.div_width) # change width to full 
                                                                                       # width after know full width
                    self.divider_lines.append(div_line)
                    self.td(div_line)  
                    self.tr()
                    
        r = self.resize()
        self.rect.w = r[0]
        self.rect.h = r[1]
        
        if self.dividers:
            for line in self.divider_lines:
                line.style.width = r[0]
                
        for item in self.string_menu_items:
            item.style.width = r[0]
            
        self.pos_func(r)    
        
        if not self.is_submenu:
            for idx, item in enumerate(self.menu_item_list):
                if self.menu_item_type[idx] == 'submenu_function':
#                    item.connect(gui.ENTER, self.check_raise_submenu, menu_item['submenu_function'], idx, item.container.rect.y)
                    item.connect(gui.ENTER, self.check_raise_submenu, self.submenu_dict[item], idx, item.container.rect.y)
                    item.connect(gui.EXIT, self.retain_hover, idx)
#                    self.submenu_dict[item] = menu_item['submenu_function']
                    
    def fm_function_callback(self,func,args):
        func(*args)
        
    def retain_hover(self, idx):
        self.menu_item_list[idx].pcls = 'hover'
        self.menu_item_list[idx].container.myhover = self.menu_item_list[idx] 
#        self.menu_item_list[idx].container.repaint()
                
    def check_raise_submenu(self, submenu_func, idx, ypos):
        if self.submenu_up:
            if self.submenu_for != idx:
                old_submenu_func = self.submenu_dict[self.menu_item_list[self.submenu_for]]
                self.menu_item_list[self.submenu_for].pcls = ''
                self.menu_item_list[self.submenu_for].container.myhover = None 
                old_submenu_func(False)
                self.submenu_for = idx
#                self.menu_item_list[idx].pcls = 'hover'
                submenu_func(True, ypos)
        else:
            self.submenu_for = idx
#            self.menu_item_list[idx].pcls = 'hover'
            submenu_func(True, ypos)
            self.submenu_up = True

    def check_hover(self):
        if self.submenu_up:
            old_submenu_func = self.submenu_dict[self.menu_item_list[self.submenu_for]]
            self.menu_item_list[self.submenu_for].pcls = ''
            self.menu_item_list[self.submenu_for].container.myhover = None 
            old_submenu_func(False)
            self.submenu_up = False
                    
    def pos_func(self, r):
        menu_width = r[0]
        menu_height = r[1]
        click_x = self.pos_info[0][0]
        click_y = self.pos_info[0][1]
        map_rect = self.pos_info[1]
        if self.is_submenu:
            map_rect2 = self.pos_info[2]
            if map_rect2.right + menu_width > map_rect.right:   # submenu off window to right 
                self.rect.x = map_rect2.left - menu_width
            else:
                self.rect.x = map_rect2.right
            if click_y + map_rect2.top + menu_height > map_rect.bottom:
                self.rect.y = map_rect.bottom - menu_height
            else:
                self.rect.y = click_y + map_rect2.top
        
        else:
            print 'pguu, pos_func', r, self.pos_info
            if click_x + menu_width > map_rect.right:
                self.rect.x = click_x - menu_width
            else:
                self.rect.x = click_x
            if click_y + menu_height > map_rect.bottom:
                self.rect.y = click_y - menu_height
            else:
                self.rect.y = click_y
            print 'pguu, pos_func2', self.rect
            


        
class FileDialogWithFilter(gui.Dialog):
    """A file picker dialog window with ability to filter displayed files."""
    
    def __init__(self, file_filter_func = None, selections_allowed = 2, title_txt="File Browser", button_txt="Okay", cls="dialog", path=None, **params):
        """FileDialog constructor.

        Keyword arguments:
            file_filter_func -- function to be called to verify whether a file should be displayed
            selections_allowed -- whether (0) selection must be a file
                                (1) selection must be a directory
                                (2) selection can be either a file or directory
            title_txt -- title text
            button_txt -- button text
            path -- initial path

        """

        cls1 = 'filedialog'
        if not path: self.curdir = os.getcwd()
        else: self.curdir = path
        params.setdefault('style',{})
        params.setdefault('theme',0)
        s = params['style']
        self.style = gui.Style(self,s, params['theme'])
        self.dir_img = gui.Image(
            gui.pguglobals.themes[self.style.theme].get(cls1+'.folder', '', 'image'))
        td_style = {'padding_left': 4,
                    'padding_right': 4,
                    'padding_top': 2,
                    'padding_bottom': 2}
        self.title = gui.Label(title_txt, cls=cls+".title.label")
        self.body = gui.Table()
        self.list = gui.List(width=350, height=150)
        self.input_dir = gui.Input()
        self.input_file = gui.Input()
        self._list_dir_()
        self.button_ok = gui.Button(button_txt)
        self.body.tr()
        self.body.td(gui.Label("Folder"), style=td_style, align=-1)
        self.body.td(self.input_dir, style=td_style)
        self.body.tr()
        self.body.td(self.list, colspan=3, style=td_style)
        self.list.connect(gui.CHANGE, self._item_select_changed_, None)
        self.button_ok.connect(gui.CLICK, self._button_okay_clicked_, None)
        self.body.tr()
        self.body.td(gui.Label("File"), style=td_style, align=-1)
        self.body.td(self.input_file, style=td_style)
        self.body.td(self.button_ok, style=td_style)
        self.value = None
        gui.Dialog.__init__(self, self.title, self.body)
        
    def _list_dir_(self):
        self.input_dir.value = self.curdir
        self.input_dir.pos = len(self.curdir)
        self.input_dir.vpos = 0
        dirs = []
        files = []
        try:
            for i in os.listdir(self.curdir):
                if os.path.isdir(os.path.join(self.curdir, i)): dirs.append(i)
                else: files.append(i)
        except:
            self.input_file.value = "Opps! no access"
        #if '..' not in dirs: dirs.append('..')
        dirs.sort()
        dirs = ['..'] + dirs
        
        files.sort()
        for i in dirs:
            #item = ListItem(image=self.dir_img, text=i, value=i)
            self.list.add(i,image=self.dir_img,value=i)
        for i in files:
            #item = ListItem(image=None, text=i, value=i)
            self.list.add(i,value=i)
        #self.list.resize()
        self.list.set_vertical_scroll(0)
        #self.list.repaintall()
        
        
    def _item_select_changed_(self, arg):
        self.input_file.value = self.list.value
        fname = os.path.abspath(os.path.join(self.curdir, self.input_file.value))
        if os.path.isdir(fname):
            self.input_file.value = ""
            self.curdir = fname
            self.list.clear()
            self._list_dir_()


    def _button_okay_clicked_(self, arg):
        if self.input_dir.value != self.curdir:
            if os.path.isdir(self.input_dir.value):
                self.input_file.value = ""
                self.curdir = os.path.abspath(self.input_dir.value)
                self.list.clear()
                self._list_dir_()
        else:
            self.value = os.path.join(self.curdir, self.input_file.value)
            self.send(gui.CHANGE)
            self.close()


#class TimedText(LabelMinSpace):
class TimedImage(gui.Image):
    def __init__(self,surf,container,x,y, call_func_after_adding, call_func_after_vanish,stay_time = 3000):
        gui.Image.__init__(self,surf)
        self.stay_time = stay_time
        self.container = container
        self.call_func_after_vanish = call_func_after_vanish
        self.call_func_after_adding = call_func_after_adding
        self.clock = pygame.time.Clock()
        self.timesince = 0
        self.total_timesince = 0
#        self.timerfunc = self.check_vanish
        self.timerfunc = self.check_anim
        self.anim_time = stay_time/100
        self.x = x
        self.y = y
        self.container.add(self, x, y)
        
        self.resize()
        self.repaint()
        call_func_after_adding()
        
    def check_vanish(self):        
        self.timesince += self.clock.tick()
        if self.timesince > self.stay_time:
            self.container.remove(self)
            self.call_func_after_vanish()
            self.timerfunc = None
        
    def check_anim(self):
        new_time = self.clock.tick()
        self.timesince += new_time
        self.total_timesince += new_time
        if self.total_timesince > self.stay_time:
            self.container.remove(self)
            self.call_func_after_vanish()
            self.timerfunc = None
            
        elif self.timesince > self.anim_time:
            self.timesince = 0
            self.container.remove(self)
            self.call_func_after_vanish()
            self.y += 1
            self.container.add(self, self.x, self.y)
            self.call_func_after_adding            
        