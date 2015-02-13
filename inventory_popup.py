from events import *
from fontdefs import *
#from gamefunctions import * 
#from copy import deepcopy
#import info_dialog_utils
import pygame
from pgu import gui
import pguutils as pguu
#import locale 
#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # vary depending on your lang/locale

#def_font = fontfbtr26
large_font = fontfbtr36
#vscroll_width = 20


class InventoryScreenWrapper(gui.Container):
#    def __init__(self, obj, viewport_rect, tp_height, allow_drag, **params):
    def __init__(self, obj, viewport_rect, tp_height, move_mode, **params):
        self.vr_w = viewport_rect.width 
        self.vr_h = viewport_rect.height
        w = int(round(0.75*self.vr_w))
        h = int(round(0.75*self.vr_h))
        gui.Container.__init__(self, width = w, height = h, **params)
        self.topbar_height = 40
        self.tp_height = tp_height
#        self.allow_drag = allow_drag
        self.move_mode = move_mode
        c2left = int(round(w/3))
        c3left = int(round(2*w/3))
        c3right = w
        self.inv_scr = InventoryScreen(obj,w,h-self.topbar_height, c2left, c3left, c3right, self)
        
        topbar = gui.Container()
        topbar.add(gui.Label(obj.name, font = large_font), 1, 1)

        topbar.add(gui.Label('Storage',font = fontfbtr36),c3left+35,1)
        done_btn = gui.Button('Done')
        dbw,dbh = done_btn.resize() 
        topbar.add(done_btn,c3right-dbw-5,self.topbar_height/2-dbh/2)
        done_btn.connect(gui.CLICK, self.on_close)
        
        self.add(topbar,0,0)
        self.add(self.inv_scr,0,self.topbar_height)
        
        left = int(round(self.vr_w/2. - w/2.))
        top = int(round(tp_height + self.vr_h/2. - h/2.))
        
        self.rect.x = left
        self.rect.y = top

    def on_close(self):
        ev = HideModalWindowEvent()
        queue.put(ev)
#        ev = SwitchToMainMapControllerEvent()
#        queue.put(ev)

    def mouse_motion_outside(self):
        for w in self.inv_scr.widgets:
            if isinstance(w,InventoryContainer):
                w._dragging = False
                w._draginprogress = False
                ev = DragInModalEvent(False)
                queue.put(ev)
                self.inv_scr.clean_up_from_drag(w)
                if w.old_panel == 'backpack':
                    self.inv_scr.add_item_to_backpack(w)
                elif w.old_panel == 'equipped':
                    self.inv_scr.add_item_to_equipped(w, w.slot)
                self.inv_scr.repaint()
                break
        


class InventoryScreen(gui.Container):
    '''
    contains 3 containers, side by side
    Left container contains a summary of stats
    Middle container contains a list of equipped items
    Right container contains a scrollable container of backpack
    (all the other items)
    
    Setting the class creation formatting background 
    to (0,0,0,0) will suppress the overall background.

    todo - allow (or use) bigger font sizes if a large
    viewport rect?
    '''
    
#    def __init__(self, obj, viewport_rect, tp_height, **params):
#        self.vr_w = viewport_rect.width 
#        self.vr_h = viewport_rect.height
#        w = int(round(0.75*self.vr_w))
#        h = int(round(0.75*self.vr_h))
    def __init__(self, obj,w,h, c2l, c3l, c3r, wrapper):
#        gui.Container.__init__(self, width = w, height = h, **params)
        gui.Container.__init__(self, width = w, height = h)
        
        self.c2left = c2l
        self.c3left = c3l
        self.c3right = c3r
        self.wrapper = wrapper
        
#        self.params = params
        self.obj = obj

        self.dnormal_style = {}
        self.dnormal_style['border_color'] = (0,0,0,0)
        self.dnormal_style['border_left'] = 1
        self.dnormal_style['border_right'] = 1
        self.dnormal_style['border_top'] = 1
        self.dnormal_style['border_bottom'] = 1
#        self.dnormal_style['background','hover'] = (5,5,255,0)

        self.allowed_style = {}
        self.allowed_style['border_color'] = (250,250,0,250)
#        self.allowed_style['border_left'] = 1
#        self.allowed_style['border_right'] = 1
#        self.allowed_style['border_top'] = 1
#        self.allowed_style['border_bottom'] = 1
#        self.allowed_style['background','hover'] = (255,255,255,70)
        self.allowed_style['background','hover'] = (140,140,255,100)

        self.bpsa_height = self.style.height - self.dnormal_style['border_top'] - self.dnormal_style['border_bottom']
         
        self.create_stats_container()
        self.create_equipped_container()
        self.create_backpack_scrollarea()
#        self.create_outer_backpack_table()
        
        self.add(self.sc,0,0)
        self.add(self.ec,self.c2left,0)
        self.add(self.bpsa,self.c3left,0)
        
#        left = int(round(self.vr_w/2. - w/2.))
#        top = int(round(tp_height + self.vr_h/2. - h/2.))
#        
#        self.rect.x = left
#        self.rect.y = top
        
        self.allowed_slots_to_drop = []
        
    def create_stats_container(self):
        w = self.c2left
        self.sc = gui.Container(width = w, height = self.style.height, background = (250,100,100,100))
        
        self.strlab = gui.Label(str(self.obj.str)) 
        self.dexlab = gui.Label(str(self.obj.dex)) 
        self.intlab = gui.Label(str(self.obj.int)) 
        self.conlab = gui.Label(str(self.obj.con)) 
        self.wislab = gui.Label(str(self.obj.wis)) 
        self.chalab = gui.Label(str(self.obj.cha)) 

        deltax1 = int(round(w/2))
        deltax2 = 38
        deltay = 15
        startx = 2
        y = 2
#        self.sc.add(gui.Label('Str: ' + str(self.obj.str)),startx,y)
        self.sc.add(gui.Label('Str:'),startx,y)
        self.sc.add(self.strlab,startx+deltax2,y)
        self.sc.add(gui.Label('Dex:'),startx+deltax1,y)
        self.sc.add(self.dexlab,startx+deltax1+deltax2,y)
        y += deltay
        self.sc.add(gui.Label('Int:'),startx,y)
        self.sc.add(self.intlab,startx+deltax2,y)
        self.sc.add(gui.Label('Con:'),startx+deltax1,y)
        self.sc.add(self.conlab,startx+deltax1+deltax2,y)
        y += deltay
        self.sc.add(gui.Label('Wis:'),startx,y)
        self.sc.add(self.wislab,startx+deltax2,y)
        self.sc.add(gui.Label('Cha:'),startx+deltax1,y)
        self.sc.add(self.chalab,startx+deltax1+deltax2,y)
        
    def create_equipped_container(self):
        w = self.c3left - self.c2left
        params2 = {'allow_receive_hover_while_sibling_drag': True}
        self.ec = gui.Container(width = w, height = self.style.height, background = (80,80,80,100),**params2)
        
        self.equip_slot_keys = ['mainhand', 
                                'offhand', 
                                'bothhands',
                                'head',
                                'storage']
        
        self.equip_slot_labels = {}
        self.equip_slot_labels['mainhand'] = gui.Label('Main hand:')
        self.equip_slot_labels['offhand'] = gui.Label('Off hand:')
        self.equip_slot_labels['bothhands'] = gui.Label('Both hands:')
        self.equip_slot_labels['head'] = gui.Label('Head:')
        self.equip_slot_labels['storage'] = gui.Label('Storage:')
        
        self.container_min_width = 130
        
        self.equipped_inv_containers = {}
        self.equipped_items = {}
        self.slot_locs = {}
        for k in self.equip_slot_keys:
#        for k,v in self.obj.items.iteritems():
 #           if k != 'storage':
            if k in self.obj.items and self.obj.items[k]:
                item = self.obj.items[k]
                self.equipped_inv_containers[k] = InventoryContainer(pguu.LabelMinSpace(item.name, width = self.container_min_width),item,k,self,'equipped')
                self.equipped_items[k] = item
            else:
                self.equipped_inv_containers[k] = InventoryContainer(pguu.LabelMinSpace('',width = self.container_min_width),None,k,self,'equipped')
                self.equipped_items[k] = None
                    
        startx = 1
        deltax = 110
        y = 1
        deltay = 22
        for k in self.equip_slot_keys:
            self.ec.add(self.equip_slot_labels[k],startx,y)
            self.ec.add(self.equipped_inv_containers[k],startx+deltax,y)
            self.slot_locs[k] = (startx+deltax,y)
            y+= deltay
            
    def remove_item_from_equipped(self, slot_name):
        old_container = self.equipped_inv_containers[slot_name]
        self.ec.remove(self.equipped_inv_containers[slot_name])
        self.equipped_inv_containers[slot_name] = InventoryContainer(pguu.LabelMinSpace('',width = self.container_min_width),None,slot_name,self,'equipped')
        self.equipped_items[slot_name] = None
        self.ec.add(self.equipped_inv_containers[slot_name], self.slot_locs[slot_name][0], self.slot_locs[slot_name][1])
        if old_container.item:
            ev = RemoveItemFromGameObjectEvent(self.obj, old_container.item, 'equipped', slot_name)
            queue.put(ev) 
        return old_container
        
    def add_item_to_equipped(self, inv_container, slot_name):
        slot_loc = self.slot_locs[slot_name]
        self.ec.add(inv_container, slot_loc[0], slot_loc[1])
        self.equipped_inv_containers[slot_name] = inv_container
        self.equipped_items[slot_name] = inv_container.item 
        inv_container.panel = 'equipped'
        inv_container.old_panel = 'equipped'
        inv_container.slot = slot_name
        inv_container.old_slot = slot_name
        ev = AddItemToGameObjectEvent(self.obj, inv_container.item, 'equipped', slot_name)
        queue.put(ev)
        
    def create_backpack_scrollarea(self):
        w = self.c3right - self.c3left
#        params2 = {'allow_receive_hover_while_sibling_drag': True}
        
#        self.bpc = gui.Container(width = w, height = self.style.height, background = (140,240,140,50), style = self.dnormal_style)
#        self.bpsa = gui.ScrollArea(self.bpc, width = w, height = self.style.height, \
#                                   hscrollbar = False, vscrollbar = True, style = self.dnormal_style)
#        self.bpc = gui.Container(width = w, height = self.style.height)
        self.bpc = gui.Container(width = w, height = self.bpsa_height)
#        self.bpsa = gui.ScrollArea(self.bpc, width = w, height = self.style.height, background = (100,100,220,100), \
#                                   hscrollbar = False, vscrollbar = True, style = self.dnormal_style)
        self.bpsa = gui.ScrollArea(self.bpc, width = w, height = self.bpsa_height, background = (100,100,220,100), \
                                   hscrollbar = False, vscrollbar = True, style = self.dnormal_style)
        
        self.bp_list = []
        for v in self.obj.items['storage'].items:
            lbl = pguu.LabelMinSpace(v.name, width = self.container_min_width)
            invslt = InventoryContainer(lbl,v,None,self,'backpack')
            self.bp_list.append((invslt, v, v.name))
#            self.bpc.add(invslt,1,y)
#            y += self.bpc_deltay
#        self.next_bpc_yval = y
        self.last_spot_spacer = gui.Spacer(width = 1, height = 1) 
        self.show_backpack()
        
    def show_backpack(self):
        for entry in self.bp_list:
            if entry[0] in self.bpc.widgets:
                self.bpc.remove(entry[0])
        if self.last_spot_spacer in self.bpc.widgets:
            self.bpc.remove(self.last_spot_spacer)
        self.bp_list.sort(key=lambda x: x[2].lower())
#        name_list.sort(key=cmp_to_key(locale.strcoll))    
#        sorted(mylist, key=cmp_to_key(locale.strcoll))             
        y = 1
        self.bpc_deltay = 22
        for entry in self.bp_list:
            self.bpc.add(entry[0],1,y)
            y += self.bpc_deltay
        self.next_bpc_yval = y
        
    def remove_item_from_backpack(self, inv_container):
        if inv_container in self.bpc.widgets:
#            self.next_bpc_yval -= self.bpc_deltay
            self.bpc.remove(inv_container)
            del_idx = -1
            for idx, bptuple in enumerate(self.bp_list):
                if bptuple[0] == inv_container:
                    del_idx = idx
                    break
            if del_idx != -1:    
                self.bp_list.pop(del_idx)
                print 'remove item', del_idx, len(self.bp_list)
                if del_idx == len(self.bp_list):
                    print 'inserting last spot spacer'
                    self.bpc.add(self.last_spot_spacer,1,self.next_bpc_yval-1)
            ev = RemoveItemFromGameObjectEvent(self.obj, inv_container.item, 'storage')
            queue.put(ev)

    def add_item_to_backpack(self, inv_container):
        if inv_container not in self.bpc.widgets:
#            self.bpc.add(inv_container, 1, self.next_bpc_yval)
#            self.next_bpc_yval += self.bpc_deltay
            self.bp_list.append((inv_container, inv_container.item, inv_container.item.name)) 
            inv_container.panel = 'backpack'
            inv_container.old_panel = 'backpack'
            inv_container.slot = None
            inv_container.old_slot = None
            self.show_backpack()
            ev = AddItemToGameObjectEvent(self.obj, inv_container.item, 'storage')
            queue.put(ev)

    def clean_up_from_drag(self, inv_container):
        self.remove(inv_container)
        for slt_name in self.equip_slot_keys:
#            if slt_name in self.allowed_slots_to_drop:
#        for slt_name in self.allowed_slots_to_drop:
            inven_container = self.equipped_inv_containers[slt_name]
            inven_container.style.theme_overrides.update(inv_container.container_style)
        self.allowed_slots_to_drop = []
        
        dnormal_style = {}
        dnormal_style['border_color'] = (250,250,250,0)
        # somehow, self.dnormal_style gets changed, so have to force it here
#        dnormal_style['background','hover'] = (0,255,0,0)
        self.bpsa.style.theme_overrides.update(dnormal_style)
#        self.bpsa.sbox.style.theme_overrides.update( {('background','hover'): (0,0,0,0)} )
        if ('background','hover') in self.bpsa.style.theme_overrides:
            del self.bpsa.style.theme_overrides[('background','hover')]
            # for some reason, just setting it to invisible doesn't work

    def set_dragging_theme(self):
        self.bpsa.style.theme_overrides.update(self.allowed_style)
    
    def calc_button_space(self):
    
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
    
    def show_nodrag_message(self):
        print '************* inv popup, show no drag *****************'
        msg = 'To change inventory, you must either be in free move mode or have used no actions yet in phased move mode.'    
#        msg = 'Problem with Targetting'
#        if 'attack_type' in self.source:
#            msg += ' for ' + self.source['attack_type'] 
#        if 'spell_name' in self.source:
#            msg += ' for ' + self.source['spell_name'] 
#        if 'obj_id' in self.source:
#            obj = self.game.objectIdDict[self.source['obj_id']]
#            msg += ' from ' + obj.name
        ev = ShowDefaultInfoPopupEvent(msg)
        queue.put(ev)
    
    
class InventoryContainer(gui.Container):
    def __init__(self, widget, item, slot, inv_screen, panel, **params):
#        if item and inv_screen.wrapper.allow_drag:
#        if item and (inv_screen.wrapper.move_mode == 'free' or \
#                     (inv_screen.wrapper.move_mode == 'phased' and inv_screen.obj.actions_used == [])):
#            params.setdefault('draggable',True)
#            params.setdefault('allow_hover_propagate_while_dragging',True)
        params.setdefault('draggable',True)
        params.setdefault('allow_hover_propagate_while_dragging',True)
        self.container_style = {}
        self.container_style['border_color'] = (100,100,100,100)
        self.container_style['border_left'] = 1
        self.container_style['border_right'] = 1
        self.container_style['border_top'] = 1
        self.container_style['border_bottom'] = 1
        self.container_style['background','hover'] = (255,255,255,50)
        params.setdefault('style',self.container_style)
        gui.Container.__init__(self, **params)
        self.add(widget,0,0)
        self.item = item
        self.i_s = inv_screen
        self.panel = panel
        self.old_panel = panel
        self.slot = slot
        self.old_slot = slot

        self.allowed_style = {}
        self.allowed_style['border_color'] = (250,250,0,250)
#        self.allowed_style['border_left'] = 1
#        self.allowed_style['border_right'] = 1
#        self.allowed_style['border_top'] = 1
#        self.allowed_style['border_bottom'] = 1
#        self.allowed_style['background','hover'] = (255,255,255,50)

        if item:
            self.connect(gui.CLICK,self.click_event)
            
    def click_event(self,_event):
        if _event.button == 3:
            self.find_my_topleft_in_inv_scr()
            self.my_topleft_in_inv_scr
            vp_x = self.my_topleft_in_inv_scr[0] + _event.pos[0] + self.i_s.rect.x + self.i_s.wrapper.rect.x
#            vp_y = self.my_topleft_in_inv_scr[1] + _event.pos[1] + self.i_s.wrapper.topbar_height + self.i_s.wrapper.tp_height
            vp_y = self.my_topleft_in_inv_scr[1] + _event.pos[1] + self.i_s.rect.y + self.i_s.wrapper.rect.y
            vp_pos = (vp_x,vp_y)
            
            ev = InventoryScreenRightClickEvent(self, vp_pos)
            queue.put(ev)
            
#        elif _event.button == 1 and not self.draggable:
#            print '************** inv popup click1 event *************'
#            self.i_s.show_nodrag_message()            


    def startdrag(self, pos):
#       pos is position within myself relative to my topleft.  
#       pos = (0,0) would refer to the topleft of me
        self._dragging = True
        self._delta = (pos[0], pos[1])
    
    def find_my_topleft_in_inv_scr(self):
        
        if self.panel == 'backpack':
            myx_in_bpc = self.rect.x
            myy_in_bpc = self.rect.y
    
            bpc = self.container
            bpcx_in_sbox = bpc.rect.x
            bpcy_in_sbox = bpc.rect.y
    
            sbox = bpc.container
            sboxx_in_td = sbox.rect.x
            sboxy_in_td = sbox.rect.y
    
            td = sbox.container
            tdx_in_sarea = td.rect.x
            tdy_in_sarea = td.rect.y
    
            sarea = td.container
            sareax_in_is = sarea.rect.x
            sareay_in_is = sarea.rect.y
            
            left = myx_in_bpc + bpcx_in_sbox + sboxx_in_td + tdx_in_sarea + sareax_in_is  
            top = myy_in_bpc + bpcy_in_sbox + sboxy_in_td + tdy_in_sarea + sareay_in_is  
#            self.my_topleft_in_inv_scr = (left,top)
            
        elif self.panel == 'equipped':
            myx_in_ec = self.rect.x
            myy_in_ec = self.rect.y
            
            ec = self.container
            ecx_in_is = ec.rect.x
            ecy_in_is = ec.rect.y
            
            left = myx_in_ec + ecx_in_is
            top = myy_in_ec + ecy_in_is
#            self.my_topleft_in_inv_scr = (left,top)

        elif self.panel == 'i_s':
            left = self.rect.x
            top = self.rect.y
            
        self.my_topleft_in_inv_scr = (left,top)
        
    def mousedown(self, _event):
        print 'invpopup, mousedown', self._dragging, self._draginprogress
        if _event.button == 1:
            if self.draggable:
                if self.item and (self.i_s.wrapper.move_mode == 'free' or \
                             (self.i_s.wrapper.move_mode == 'phased' and self.i_s.obj.actions_used == [])):
                
                    self.drag_number = 1 
                    keymods = pygame.key.get_mods()
                    if keymods & KMOD_CTRL:
                        self.drag_number = 5
                    elif keymods & KMOD_SHIFT:
                        self.drag_number = 'all'
                    elif keymods & KMOD_CTRL and keymods & KMOD_SHIFT:
                        self.drag_number = 20        
                    self.startdrag(_event.pos)
                    self.clearotherdrags()
                else:
                    self.i_s.show_nodrag_message()
            
        if self.focusable and not self.iscontainer:
            self._dragging = False
            self.clearotherdrags()

    def mouseup(self, _event):
#        if _event.button == 1 and self._dragging:
        print 'invpopup, mouseup', self._dragging, self._draginprogress
        if _event.button == 1:
            if self._dragging:
                self._dragging = False
                if self._draginprogress:
                    self._draginprogress = False
                    ev = DragInModalEvent(False)
                    queue.put(ev)
                    valid_drop = False
                    hovered_inv_container = self.i_s.ec.myhover
                    if hovered_inv_container:    
                        slot_name = hovered_inv_container.slot
                        if slot_name in self.i_s.allowed_slots_to_drop:     # dropping on valid equip slot
                            valid_drop = True
                            self.i_s.clean_up_from_drag(self)
                            return_loc = 'backpack'
                            if self.old_panel == 'equipped':
                                return_loc = 'equipped'
                            container_that_was_in_spot = self.i_s.remove_item_from_equipped(slot_name)
                            if container_that_was_in_spot.item:
                                if return_loc == 'backpack':
                                    self.i_s.add_item_to_backpack(container_that_was_in_spot)
                                elif return_loc == 'equipped':
                                    returning_item = container_that_was_in_spot.item
                                    if self.slot in returning_item.allowed_slots: 
                                        self.i_s.add_item_to_equipped(container_that_was_in_spot,self.slot)
                                    else:
                                        self.i_s.add_item_to_backpack(container_that_was_in_spot)
                            elif return_loc == 'backpack':      # moving from backpack to empty slot
                                self.i_s.show_backpack()
                            self.i_s.add_item_to_equipped(self,slot_name)
                            self.i_s.repaint()
                    
                    elif self.i_s.myhover == self.i_s.bpsa \
                    and 'backpack' in self.i_s.allowed_slots_to_drop: # dropping on backpack
                        valid_drop = True
                        self.i_s.clean_up_from_drag(self)
                        self.i_s.add_item_to_backpack(self)
                        self.i_s.repaint()
        
                    if not valid_drop:   # not a valid drop, return to original spot
                        self.i_s.clean_up_from_drag(self)
                        if self.old_panel == 'backpack':
                            self.i_s.add_item_to_backpack(self)
                        elif self.old_panel == 'equipped':
                            self.i_s.add_item_to_equipped(self, self.slot)
                        self.i_s.repaint()
                
    def mousemove(self, _event):
        # if we have a shape, but haven't started dragging yet
        print 'invpopup, mousemove', self._dragging, self._draginprogress, _event.pos
        if self._dragging: 
            pt = _event.pos
            if not self._draginprogress:
    
                # only start the drag after having moved a couple pixels
                tolerance = 0
#                dx = abs(pt[0] - self._dragStartPos[0])
#                dy = abs(pt[1] - self._dragStartPos[1])
                dx = abs(pt[0] - self._delta[0])
                dy = abs(pt[1] - self._delta[1])
                if dx <= tolerance and dy <= tolerance:
                    print 'invpopup, mousemove2'
                    return
    
                self._draginprogress = True
                self.find_my_topleft_in_inv_scr()
                tl = self.my_topleft_in_inv_scr
                if self.panel == 'backpack':
                    self.i_s.remove_item_from_backpack(self)
                elif self.panel == 'equipped':
                    self.i_s.remove_item_from_equipped(self.slot)
                self.i_s.add(self,tl[0],tl[1])
                self.i_s.focus(self)
                self.rect.x = tl[0]
                self.rect.y = tl[1]
                self.i_s.allowed_slots_to_drop = self.i_s.obj.find_allowed_drop_slots(self.item)
#                self.i_s.allowed_slots_to_drop.extend(self.item.allowed_slots)
                for slot_name in self.i_s.equip_slot_keys:
                    inv_container = self.i_s.equipped_inv_containers[slot_name]
                    if slot_name in self.i_s.allowed_slots_to_drop:
                        inv_container.style.theme_overrides.update(self.allowed_style)
                    else:
                        inv_container.style.theme_overrides.update( { ('background','hover'): (0,0,0,0) } )
                if 'backpack' in self.i_s.allowed_slots_to_drop: 
                    self.i_s.set_dragging_theme()
                self.panel = 'i_s'
                ev = DragInModalEvent(True)
                queue.put(ev)
                
                
            if self._draginprogress:
#                self.find_my_topleft_in_inv_scr()
#                rect = self.my_topleft_in_inv_scr
                rect = self.rect
#                self.container.repaint((rect.x,rect.y,rect.w,rect.h))
                fp = (rect[0] + pt[0] - self._delta[0], rect[1] + pt[1] - self._delta[1])
                cr = self.container.rect
                if fp[0] < self.i_s.c2left:
                    self.rect.left = self.i_s.c2left
                    if pt[0] > 0:
                        self._delta = (pt[0], self._delta[1])
                    else:
                        self._dragging = False
                elif fp[1] < 0:
                    self.rect.top = 0
                    if pt[1] > 0:
                        self._delta = (self._delta[0], pt[1])
                    else:
                        self._dragging = False
                elif fp[0]+rect.width > cr.width:
                    self.rect.right = cr.width
                    if pt[0] + rect[0] < cr.width-1:
                        self._delta = (pt[0], self._delta[1])
                    else:
                        self._dragging = False
                elif fp[1] + rect.height > cr.height:
                    self.rect.bottom = cr.height
                    if pt[1] + rect[1] < cr.height-1:
                        self._delta = (self._delta[0], pt[1])
                    else:
                        self._dragging = False
                else:
                    self.rect.topleft = fp
                    
                if self._dragging:
                    self.style.x = self.rect.x
                    self.style.y = self.rect.y
                else:
                    self._draginprogress = False
                    ev = DragInModalEvent(False)
                    queue.put(ev)
                    self.i_s.clean_up_from_drag(self)
                    if self.old_panel == 'backpack':
                        self.i_s.add_item_to_backpack(self)
                    elif self.old_panel == 'equipped':
                        self.i_s.add_item_to_equipped(self, self.slot)
                    self.i_s.repaint()
                    
                self.repaint()
        
        
    

        
