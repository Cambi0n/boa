import pygame
from pgu import gui
from fontdefs import *




class InfoDialog(gui.Dialog):
#class InfoDialog(gui.Table):
    '''
    dialog is a table which has a title bar and a container.
    '''
    def __init__(self,title,c,**params):
        
        self.title = gui.Label(title)
        self.c = c
                        
        gui.Dialog.__init__(self,self.title,self.c,**params)
#        gui.Table.__init__(self, **params)
#        self.td(self.c)

class VertScrollArea(gui.ScrollArea):
    '''
    ScrollArea is a table which contains a slidebox which contains a 
    widget.  This widget is usually a container of some kind, and is
    the value passed in as c.
    
    The width of the widget should be a little less than the width
    of the ScrollArea so it doesn't run into the scroll bar.
    '''
    def __init__(self,c,**params):
        self.c = c
        gui.ScrollArea.__init__(self, self.c, width = self.c.style.width+20, height = 200, hscrollbar = False,**params)
    
    
def writewrap(s, text, font=None, rect=None, color = None, maxlines=None, wrapchar=False):
    """Write wrapped text on a pygame surface.

    maxlines -- specifies the maximum number of lines to write 
        before stopping
    wrapchar -- whether to wrap at the character level, or 
        word level
        
    if rect passed in, text is placed in 'rect' location on surface.  If not, then rect = surface rect.
    
    If text exceeds boundaries of rect before maxlines invoked, then text continues to be written outside
    boundaries of rect.  todo - fix this
    
    If rect input parameter goes outside bounds of surface, text can be written outside surface.  todo - fix this
    """

    if font:
        use_font = font
    else:
        use_font =  pygame.font.Font(None,12)
    if color:
        use_color = color
    else:
        use_color = (255,255,255,255)
    if rect:
        use_rect = rect
    else:
        use_rect = s.get_rect()
    
    txt = text
    txt = txt.replace("\t", " "*8)
    tmp = use_font.render(" ", 1, use_color)
    sw,sh = tmp.get_size()
    y = use_rect.top
    row = 1
    done = False
    for sentence in txt.split("\n"):
        x = use_rect.left
        if wrapchar:
            words = sentence
        else:
            words = sentence.split(" ")
            
        for word in words:
            if (not wrapchar):
                word += " "
            tmp = use_font.render(word, 1, use_color)
            (iw, ih) = tmp.get_size()
            if (x+iw > use_rect.right):
                x = use_rect.left
                y += sh
                row += 1
                if (maxlines != None and row > maxlines):
                    done = True
                    break
            s.blit(tmp, (x, y))
            #x += iw+sw
            x += iw
        if done:
            break
        y += sh
        row += 1
        if (maxlines != None and row > maxlines):
            break

    return use_rect.width, x, y-sh, sh

def return_msg_on_surface(msg, max_width, max_height, background = (0,0,0,0), font = fontdefault22, fontcolor = (255,255,255,255)):
    # msg can be either a simple string, or it can be a list as described below
    # if a simple string, then background, font, and fontcolor from passed parameters are used
    # if list, format is:
    #    msg = []
    #    msg.append(string_fragment_dict)
    #        where string_fragment_dict is:
    #            string_fragment_dict['string'] = some text 
    #            string_fragment_dict['color'] = (200,200,0,255)    (optional)
    #            string_fragment_dict['font'] = def_font            (optional)
    #    msg.append(next string_fragment_dict)
    # the elements of msg are then placed in sequence on the surface, wrapping if necessary.
    # if a string_fragment_dict contains only 'string' key, then background, font, and fontcolor from
    # passed parameters are used
    # max_width and max_height describe the maximum size of the surface.  The resulting surface
    # might be smaller than this, but it won't be larger.  Text that might have been placed
    # outside this space simply isn't shown.
    
    pygame_surf = pygame.Surface((max_width,max_height)).convert()
    xmax,ymax,row_heights = writewrap2(pygame_surf, msg, color = fontcolor, font = font)
    pygame_surf = pygame.Surface((xmax,ymax)).convert_alpha()
    pygame_surf.fill( background )
    writewrap3(pygame_surf, msg, row_heights, color = fontcolor, font = font)
    
    return pygame_surf
    
    
def writewrap2(s, text, font=None, rect=None, color = None, wrapchar=False):
    """Write wrapped text on a pygame surface.

    maxlines -- specifies the maximum number of lines to write 
        before stopping
    wrapchar -- whether to wrap at the character level, or 
        word level
    """

    if font:
        default_font = font
    else:
        default_font =  pygame.font.Font(None,12)
    if color:
        default_color = color
    else:
        default_color = (255,255,255,255)
    if rect:
        default_rect = rect
    else:
        default_rect = s.get_rect()
        
    if type(text) is str:
        text_list = [{'string':text,'font':default_font,'color':default_color}]
    elif type(text) is list:
        text_list = text
    else:
        return s
        
    y = default_rect.top
#    row = 1
    done = False
    sh = 0
    row_heights = []
    max_w = 0
    temp_s = s.copy()
    x = default_rect.left
    for text_seg in text_list:
        if 'string' not in text_seg:
            break
        else:
            txt = text_seg['string']
        if 'font' not in text_seg:
            use_font = default_font
        else:
            use_font = text_seg['font']
        if 'color' not in text_seg:
            use_color = default_color
        else:
            use_color = text_seg['color']
        
        txt = txt.replace("\t", " "*8)
        tmp = use_font.render(" ", 1, use_color)
        sw,new_sh = tmp.get_size()
        if new_sh > sh:
            sh = new_sh
        for sentence in txt.split("\n"):
#            x = use_rect.left
            if wrapchar:
                words = sentence
            else:
                words = sentence.split(" ")
                
            for word in words:
                if (not wrapchar):
                    word += " "
                tmp = use_font.render(word, 1, use_color)
                (iw, ih) = tmp.get_size()
                if (x+iw > default_rect.right):
                    y += sh
                    if y > default_rect.bottom:
                        done = True
                        break
                    if x+iw > default_rect.right:
                        y -= sh
                        continue        # skip the extra long word
                    x = default_rect.left
                    row_heights.append(sh)
                    tmp2 = use_font.render(" ", 1, use_color)
                    sw,sh = tmp2.get_size()
                temp_s.blit(tmp, (x, y))
                x += iw
                max_w = max(max_w, x)
            if done:
                break
            x = default_rect.left
            y += sh
            row_heights.append(sh)
            
    return max_w,y,row_heights
            
def writewrap3(s, text, row_heights, font=None, rect=None, color = None, wrapchar=False):
    """Write wrapped text on a pygame surface.

    maxlines -- specifies the maximum number of lines to write 
        before stopping
    wrapchar -- whether to wrap at the character level, or 
        word level
    """

    if font:
        default_font = font
    else:
        default_font =  pygame.font.Font(None,12)
    if color:
        default_color = color
    else:
        default_color = (255,255,255,255)
    if rect:
        default_rect = rect
    else:
        default_rect = s.get_rect()
        
    if type(text) is str:
        text_list = [{'string':text,'font':default_font,'color':default_color}]
    elif type(text) is list:
        text_list = text
    else:
        return s
        
    # do it all again, but this time center each word vertically on its line
    y = default_rect.top
    done = False
    row = 0
    this_height = row_heights[row]
    x = default_rect.left
    for text_seg in text_list:
        if 'string' not in text_seg:
            return s
        else:
            txt = text_seg['string']
        if 'font' not in text_seg:
            use_font = default_font
        else:
            use_font = text_seg['font']
        if 'color' not in text_seg:
            use_color = default_color
        else:
            use_color = text_seg['color']
        
        txt = txt.replace("\t", " "*8)
        tmp = use_font.render(" ", 1, use_color)
        sw,sh = tmp.get_size()
        for sentence in txt.split("\n"):
#            x = use_rect.left
            if wrapchar:
                words = sentence
            else:
                words = sentence.split(" ")
                
            for word in words:
                if (not wrapchar):
                    word += " "
                tmp = use_font.render(word, 1, use_color)
                (iw, ih) = tmp.get_size()
                if (x+iw > default_rect.right):
                    y += this_height
                    if y > default_rect.bottom:
                        done = True
                        break
                    if x+iw > default_rect.right:
                        y -= this_height
                        continue        # skip the extra long word
                    row += 1
                    this_height = row_heights[row]
                    x = default_rect.left
                if sh < this_height:
                    this_y_lowering = (this_height - sh)/2
                else:
                    this_y_lowering = 0
                s.blit(tmp, (x, y+this_y_lowering))
                x += iw
            if done:
                break
            x = default_rect.left
            y += this_height


    

    