
import pygame
from pgu import gui

from events import *
from fontdefs import *
#from gamefunctions import * 
#from copy import deepcopy
import info_dialog_utils
import pguutils as pguu
import view_utils

def_font = fontfbtr26
large_font = fontfbtr36
vscroll_width = 20

def set_object_info_popup_data(obj, game, sel_obj = None):
    '''
    raw_data is dictionary with 'text' and 'buttons' keys
    'text' has sequential keys.  Each of these has 'string',
    'color' (optional), and 'font' (optional).  The wordwrap
    function will be used to place this text.
    
    raw_data can also have 'text_panel_format' and 
    'button_panel_format' keys.  The values for these are
    dictionaries of format.
    
    'buttons' has sequential keys.  Each of these has 
    'contents' for value of button, and 'function'
    for function to call when pressing button.
    A special entry for 'function' is 'close' to
    close the popup.  Buttons can also have a
    'format' key.
    '''
    
    if obj.objtype == 'monster':
    
        raw_data = {}
        raw_data['text'] = {}
        raw_data['text'][0] = {}
        
        effect_str = ''
        for effect_entry in obj.temporary_effects:
            effect = effect_entry[0]
            effect_str += effect[0] + ' '   

        if sel_obj:
            monpos = obj.pos
            charpos = sel_obj.pos
            map_section_name = sel_obj.map_section 
            cover, soft_cover = view_utils.cover_between_two_tiles(charpos, monpos, map_section_name, game, True, {})

            raw_data['text'][0]['string'] = obj.display_name + "\n" \
                + effect_str + "\n" \
                + obj.show_current_hp_description() + "\n" \
                + "cover = " + str(cover) + ", soft cover = " + str(soft_cover)
                
        else:
            raw_data['text'][0]['string'] = obj.display_name + "\n" \
                + effect_str + "\n" \
                + obj.show_current_hp_description()
              
        
        
        '''        "This is information about the monster.  It is \
        a very scary monster.  I don't think you should attack it \
        unless you want to die!!!\n\n\
        But if you want to try it, go ahead.  Be my guest. \
        But it really is very scary.\n\n\
        This is information about the monster.  It is \
        a very scary monster.  I don't think you should attack it \
        unless you want to die!!!\n\n\
        But if you want to try it, go ahead.  Be my guest. \
        But it really is very scary. \n\n\
        This is information about the monster.  It is \
        a very scary monster.  I don't think you should attack it \
        unless you want to die!!!\n\n\
        But if you want to try it, go ahead.  Be my guest. \
        But it really is very scary."
        '''

        raw_data['text'][0]['color'] = (200,200,0,255)
        raw_data['text'][0]['font'] = def_font
        raw_data['text_panel_format'] = {'background': (50,0,150,50)}
        
        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
        raw_data['buttons'] = {}
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
        raw_data['buttons'][0]['function'] = 'close'
    #    raw_data['buttons'][0]['format'] = {'background':(250,0,0,150)}
    
    elif obj.objtype == 'playerchar':
        raw_data = {}
        raw_data['text_panel_format'] = {'background': (50,0,150,50)}
        raw_data['text'] = {}
        raw_data['text'][0] = {}
        class_level_str = ''
        first = True
        for c,l in obj.advclasses.iteritems():
            if not first:
                class_level_str += ', '
            class_level_str += c
            class_level_str += ' '
            class_level_str += str(l)
            first = False
        effect_str = ''
        for effect_entry in obj.temporary_effects:
            effect = effect_entry[0]
            time_left = int(round((effect[1] - game.Time)/1000.))
            effect_str += effect[0] + ' for ' + str(time_left) + ' more seconds.'  
        
        raw_data['text'][0]['string'] = obj.name + ", " + obj.race + "\n" \
            + class_level_str + "\n" \
            + effect_str + "\n" \
            + 'Armor Class: ' + str(obj.calc_armor_class()) + "\n" \
            + 'Hit Points: ' + str(obj.find_current_hit_points())

        raw_data['text'][0]['color'] = (250,250,0,255)
        raw_data['text'][0]['font'] = def_font

        
        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
        raw_data['buttons'] = {}
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
        raw_data['buttons'][0]['function'] = 'close'
    #    raw_data['buttons'][0]['format'] = {'background':(250,0,0,150)}
    
    elif obj.objtype == 'carried_item':
    
        raw_data = {}
        raw_data['text'] = {}
        raw_data['text'][0] = {}
        raw_data['text'][0]['string'] = obj.display_name + "\n" \
            + str(obj.find_current_hit_points()) + " HP" 
        
        raw_data['text'][0]['color'] = (200,200,0,255)
        raw_data['text'][0]['font'] = def_font
        raw_data['text_panel_format'] = {'background': (50,0,150,50)}
        
        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
        raw_data['buttons'] = {}
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
        raw_data['buttons'][0]['function'] = 'close'
     
    return raw_data

def set_terrain_info_popup_data(map_section_name, mappos, game):
    map_section = game.map[map_section_name]
    map_spec = map_section[(mappos[0],mappos[1])]
    raw_data = {}
    raw_data['text'] = {}
    raw_data['text'][0] = {}
    raw_data['text'][0]['string'] = map_spec[0] + ', ' + map_spec[1] 

    raw_data['text'][0]['color'] = (200,200,0,255)
    raw_data['text'][0]['font'] = def_font
    raw_data['text_panel_format'] = {'background': (50,0,150,50)}
    
    raw_data['button_panel_format'] = {'background':(50,50,50,150)}
    raw_data['buttons'] = {}
    raw_data['buttons'][0] = {}
    raw_data['buttons'][0]['contents'] = gui.Label('Ok')
    raw_data['buttons'][0]['function'] = 'close'

    return raw_data
    


def set_choose_target_popup_data(msg, cancel_func, accept_func = None):

    raw_data = {}
    raw_data['text'] = {}
    raw_data['text'][0] = {}
    raw_data['text'][0]['string'] = msg 
    raw_data['text'][0]['color'] = (200,200,200,255)
    raw_data['text'][0]['font'] = fontdefault20
    raw_data['text_panel_format'] = {'background': (0,0,250,255)}
    
    raw_data['button_panel_format'] = {'background':(50,50,50,150)}
    raw_data['buttons'] = {}
    
    if accept_func:
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Accept')
        raw_data['buttons'][0]['function'] = accept_func
        cancel_spot = 1
    else:
        cancel_spot = 0
    
    raw_data['buttons'][cancel_spot] = {}
    raw_data['buttons'][cancel_spot]['contents'] = gui.Label('Cancel')
    raw_data['buttons'][cancel_spot]['function'] = cancel_func
    
#    raw_data['buttons'][0]['format'] = {'background':(250,0,0,150)}

    return raw_data
    


class PopupWithOneColumnTextAndButtonsBelow(gui.Table):
    '''
    see set_object_info_popup_data for raw_data description
    
    sizes is a tuple with 5 entries:
        suggested width as fraction of viewport_rect
        suggested height
        max width
        max height
        True if, when text exceeds max width and height, to use
            suggested size and vertical scrollbar.  False means to use
            max size and vertical scrollbar.
            
    formatting can be done by formatting at the time 
    of class creation (so called from elsewhere). 
    In this case, both the upper text table and the
    lower button table will have the same formatting.
    Alternatively, formatting can come from 
    the raw_data input variable.  In this case, the upper
    and lower tables can have different formatting.  Using
    both will tend to overlay the formatting.  Setting
    the class creation formatting background to (0,0,0,0)
    will suppress the overall background.
            
    todo - create one_column, two_column, and three_column versions of the
    format functions.  There will probably be a variety of the
    set functions, and each will then be used with the correct
    format function.
    '''
    def __init__(self,raw_data,sizes,viewport_rect,tp_height,**params):
        gui.Table.__init__(self, **params)
        
        self.raw_data = raw_data
        self.params = params
        
        self.vr_w = viewport_rect.width 
        self.vr_h = viewport_rect.height
        self.sugg_w = int(round(sizes[0]*self.vr_w))
        self.sugg_h = int(round(sizes[1]*self.vr_h))
        self.max_w = int(round(sizes[2]*self.vr_w))
        self.max_h = int(round(sizes[3]*self.vr_h))

        but_table = self.calc_button_space()
        if but_table:
            btw,bth = but_table.resize()
        else: 
            btw,bth = 0,0
        
        ttxt = raw_data['text'][0]['string']
        tcolor = raw_data['text'][0]['color']
        tfont = raw_data['text'][0]['font']
#        use_width = int(round(self.vr_w/4))
        use_width = self.sugg_w
        pygame_surf = pygame.Surface((use_width,self.vr_h*10)).convert()
        full_x_pix, final_x_pix, all_but_last_line_y_pix, one_line_y_pix = info_dialog_utils.writewrap(pygame_surf, ttxt, color = tcolor, font = tfont)
        approx_sq_pix =  all_but_last_line_y_pix * full_x_pix + one_line_y_pix*final_x_pix
        tot_height = all_but_last_line_y_pix + one_line_y_pix
        if tot_height > self.max_h:
            use_height = self.max_h
            vscroll = True
        else:
            use_height = tot_height
            vscroll = False
            
        if vscroll:
            add_width = vscroll_width
        else:
            add_width = 0
        
        params['background'] = (0,0,0,0)
        pygame_surf = pygame.Surface((use_width,tot_height)).convert_alpha()
        pygame_surf.fill( (0,0,0,0) )
        info_dialog_utils.writewrap(pygame_surf, ttxt, color = tcolor, font = tfont)
        
        if 'text_panel_format' in raw_data:
            use_params = raw_data['text_panel_format']
        else:
            use_params = params  
        
        scroll_area = gui.ScrollArea(gui.Image(pygame_surf), width = use_width+add_width, \
                                              height = use_height, hscrollbar = False, vscrollbar = vscroll,**use_params)
#        else:
#            scroll_area = gui.ScrollArea(gui.Image(pygame_surf), width = use_width+add_width, \
#                                              height = use_height, hscrollbar = False, vscrollbar = vscroll,**raw_data['text_panel_format'])
            
#        scroll_area = gui.ScrollArea(gui.Image(pygame_surf), width = use_width+add_width, \
#                                              height = use_height, hscrollbar = False, vscrollbar = vscroll,**params)
#        vscroll = info_dialog_utils.VertScrollArea(text_image)
#        info_popup = info_dialog_utils.InfoDialog('Information',vscroll)
#        self.pguctrl.c.open(info_popup)
        self.tr()
        self.td(scroll_area)
#        self.td(gui.Image(pygame_surf))
        if but_table:
            but_table.style.width = use_width + add_width
            but_table.resize()
            self.tr()
            self.td(but_table)
        
        left = int(round(self.vr_w/2. - use_width/2.))
        top = int(round(tp_height + self.vr_h/2. - (use_height+bth)/2.))
        
        self.rect.x = left
        self.rect.y = top
        self.rect.w = use_width
        self.rect.h = use_height + bth
        
    def calc_button_space(self):
        
        if 'buttons' in self.raw_data:
        
            buts_data = self.raw_data['buttons']
            if 'button_panel_format' in self.raw_data:
                use_params = self.raw_data['button_panel_format']
            else:
                use_params = self.params
            b_table = gui.Table(**use_params)
                
            num_buttons = len(buts_data) 
            if num_buttons > 5:   
                # use two rows
                num_in_first_row = int(round(num_buttons/2))
            else:
                num_in_first_row = num_buttons+1
            but_num = 0
            for but_data in buts_data.itervalues():
                but_num += 1
                if 'format' in but_data:
                    b_button = gui.Button(but_data['contents'], **but_data['format'])
                else:
                    b_button = gui.Button(but_data['contents'])
                if but_data['function'] == 'close':
                    b_button.connect(gui.CLICK,self.on_close)
                else:
                    b_button.connect(gui.CLICK, but_data['function'])
                b_table.td(b_button)
                if but_num >= num_in_first_row:
                    b_table.tr()
            return b_table
        else:
            return None
    
    def on_close(self):
        ev = HideModalWindowEvent()
        queue.put(ev)
#        ev = SwitchToMainMapControllerEvent()
#        queue.put(ev)
        


class ChoicePopup(gui.Table):
    '''
    Rectangular buttons, with cancel button at bottom
    todo - make this better
    '''
    def __init__(self,raw_data,choice_func,sizes,viewport_rect,tp_height,ctrl = None,**params):
        gui.Table.__init__(self, **params)
        
        self.raw_data = raw_data
        self.choice_func = choice_func
        self.params = params
        self.ctrl = ctrl
        
        self.vr_w = viewport_rect.width 
        self.vr_h = viewport_rect.height
#        self.sugg_w = int(round(sizes[0]*self.vr_w))
#        self.sugg_h = int(round(sizes[1]*self.vr_h))
#        self.max_w = int(round(sizes[2]*self.vr_w))
#        self.max_h = int(round(sizes[3]*self.vr_h))

        but_table = self.calc_button_space()
        if but_table:
            btw,bth = but_table.resize()
        else: 
            btw,bth = 0,0
        
        title = raw_data['title']
        self.td(gui.Label(title))
        
        self.btn_style = {}
        self.btn_style['background','hover'] = (140,140,255,100)
        
        choices_list = raw_data['choices']
#        choices_dict = raw_data['choices']
        for idx,v in enumerate(choices_list):
#        for k,v in choices_dict.iteritems():
            self.tr()
            
            btn = pguu.BmpButton(gui.Label(v), style = self.btn_style, theme = 'gui2theme')
            btn.connect(gui.CLICK, self.choice_made, idx)
            self.td(btn)

        if but_table:
            but_table.resize()
            self.tr()
            self.td(but_table)

        w,h = self.resize()
        
        left = int(round(self.vr_w/2. - w/2.))
#        top = int(round(tp_height + self.vr_h/2. - (h+bth)/2.))
        top = int(round(tp_height + self.vr_h/2. - (h)/2.))
        
        self.rect.x = left
        self.rect.y = top
        self.rect.w = w
#        self.rect.h = h + bth
        self.rect.h = h
        
    def choice_made(self, k):
        self.on_close()
        self.choice_func(k)
                
    def calc_button_space(self):
        
        use_params = self.params
        b_table = gui.Table(**use_params)
        b_button = gui.Button(gui.Label('Cancel'))
        b_button.connect(gui.CLICK,self.on_close)
        b_table.td(b_button)
        return b_table
    
    def on_close(self):
        ev = HideModalWindowEvent()
        self.ctrl.hide_modal_window(ev)
#        queue.put(ev)
#        ev = SwitchToMainMapControllerEvent()
#        queue.put(ev)
        


    
    

        
    