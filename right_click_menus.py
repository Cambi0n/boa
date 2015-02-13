
from events import *
from fontdefs import *
from copy import deepcopy
import pygame
from pgu import gui
from gamefunctions import * 
import info_popup, inventory_popup
import spells
import object_utils


class RightClickMenus():
    def __init__(self, evManager, uv):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
    
        self.uv = uv
        self.view = self.uv.view
        self.pguctrl = self.uv.pguctrl
        
        self.default_data = {}
        self.default_data['default'] = {}
#        self.default_data['default']['font'] = fontfbtr26
        self.default_data['section'] = {}
        self.default_data['section'][1] = {}

        self.def_font = fontfbtr26

#        self.primary_modal_window_rect = None
        
        '''    example data spec
        data = {}
        data['default'] = {}
        data['default']['font'] = fontfbtr26
        data['title'] = {}
        data['title']['string'] = 'title here'
        
        data['section'] = {}
        data['section']['divider'] = {}
        data['section'][1] = {}   
        data['section'][1][1] = {}
        data['section'][1][1]['string'] = 'item 1'
        data['section'][1][1]['font'] = fontfbtr26
        data['section'][1][1]['function'] = self.printsomething   
        data['section'][1][2] = {}
        data['section'][1][2]['string'] = 'item 2'
        data['section'][1][2]['function'] = self.printsomething   
        data['section'][1][3] = {}
        data['section'][1][3]['string'] = 'item 3     >>'
        data['section'][1][3]['submenu_function'] = self.submenu_test   
        
        pfm = self.pguctrl.create_primary_floating_menu(data, (clickpos, self.view.mapViewPortRect))
        self.view.primary_floating_menu_rect = pfm.rect
        '''

        
    def initial_right_click_processing(self, sp, clickpos):
        if self.view.selectedSprite == sp:        # only own chars can be selected
            self.sel_obj = self.view.selectedSprite.object
            self.obj = self.sel_obj
            if not (self.game.move_mode == 'free' and self.obj.orders):
                self.eval_own_char_right_click(clickpos)
        elif self.view.selectedSprite:
            self.sel_obj = self.view.selectedSprite.object
            if hasattr(sp, 'object'):
                self.obj = sp.object
#                if self.obj.objtype == 'carried_item':
#                    self.eval_carried_item_right_click(clickpos)
#                else:                                
#                    self.show_object_info()
                self.show_object_info()
        else:
            self.sel_obj = None
            if hasattr(sp, 'object'):
                self.obj = sp.object
                self.show_object_info()

    def eval_own_char_right_click(self, clickpos):
        standard_act_avail = False 
        move_act_avail = False 
        
        data = deepcopy(self.default_data)
        data['default']['font'] = self.def_font
        self.num_menu_items += 1
        data['section'][1][self.num_menu_items] = {}
        data['section'][1][self.num_menu_items]['string'] = 'Information'
        data['section'][1][self.num_menu_items]['function'] = self.show_object_info
        
        self.num_menu_items += 1
        data['section'][1][self.num_menu_items] = {}
        data['section'][1][self.num_menu_items]['string'] = 'Inventory'
        data['section'][1][self.num_menu_items]['function'] = self.show_inventory_screen

        allowed_actions = self.sel_obj.find_allowed_actions()
        
        if 'standard' in allowed_actions:
            standard_act_avail = True
        if 'move' in allowed_actions:
            move_act_avail = True 
            
        if standard_act_avail and self.sel_obj.concentration_data:
            self.num_menu_items += 1
            self.add_concentration_item(data, self.num_menu_items)
            
        if self.view.hover_sprite_dict['carried_item']:
            if move_act_avail:
                self.num_menu_items += 1
                self.add_pickup_menu_item(data, self.num_menu_items)

        if self.sel_obj.spells_memorized:
            if standard_act_avail:
                self.num_menu_items += 1
                self.add_cast_spell_menu_item(data, self.num_menu_items)
                
        enemies_in_melee_range = False  # todo - create this function
        if enemies_in_melee_range and standard_act_avail:
            self.num_menu_items += 1
            self.add_regular_attack_menu_item(data, self.num_menu_items)
            
        self.show_menu(data, clickpos)    
        
#        if standard_act_avail and self.sel_obj.concentration_data:
#            msg = "Reminder: This character has the option to maintain an existing \
#spell by using a standard action and concentrating."
#            self.view.show_default_info_popup(msg)
            
#            data = {}
#            data['default'] = {}
#            data['default']['font'] = fontfbtr26
#            data['title'] = {}
#            data['title']['string'] = 'title here'
#            
#            data['section'] = {}
#            data['section']['divider'] = {}
#            data['section'][1] = {}   
#            data['section'][1][1] = {}
#            data['section'][1][1]['string'] = 'item 1'
#            data['section'][1][1]['font'] = fontfbtr26
#            data['section'][1][1]['function'] = self.printsomething   
#            data['section'][1][2] = {}
#            data['section'][1][2]['string'] = 'item 2'
#            data['section'][1][2]['function'] = self.printsomething   
#            data['section'][1][3] = {}
#            data['section'][1][3]['string'] = 'item 3     >>'
#            data['section'][1][3]['submenu_function'] = self.submenu_test   
            
#            pfm = self.pguctrl.create_primary_floating_menu(data, (clickpos, self.view.mapViewPortRect))
#            self.view.primary_floating_menu_rect = pfm.rect
        
                    
    def eval_monster_right_click(self, clickpos):
#        self.obj = object
#        self.sel_sp = sel_sp
        adjacent = False
        standard_act_avail = False 
        data = deepcopy(self.default_data)
        data['default']['font'] = self.def_font
        
        self.num_menu_items += 1
        data['section'][1][self.num_menu_items] = {}
        data['section'][1][self.num_menu_items]['string'] = 'Information'
        data['section'][1][self.num_menu_items]['function'] = self.show_object_info

        if self.sel_obj:
#            self.sel_obj = sel_sp.object
            if self.sel_obj.objtype == 'playerchar': 
                if self.obj.pos in findAdjTiles(self.sel_obj.lastOrderedPos[0], self.sel_obj.lastOrderedPos[1], self.game.map[self.sel_obj.map_section]):
                    adjacent = True
    
                if 'standard' not in self.sel_obj.actions_used \
                and 'partial_standard' not in self.sel_obj.actions_used \
                and 'full' not in self.sel_obj.actions_used:
                    standard_act_avail = True 
                    
                if adjacent and standard_act_avail:            
                    self.num_menu_items += 1
                    self.add_regular_attack_menu_item(data, self.num_menu_items)
                    
                if self.sel_obj.spells_memorized:
                    if standard_act_avail:
                        self.num_menu_items += 1
                        self.add_cast_spell_menu_item(data, self.num_menu_items)
          
        self.show_menu(data, clickpos)    
            
    def add_regular_attack_menu_item(self,data, menu_item_number):
        data['section'][1][menu_item_number] = {}
        data['section'][1][menu_item_number]['string'] = 'Attack'
        data['section'][1][menu_item_number]['function'] = self.add_standard_melee_attack_order
        
    def add_standard_melee_attack_order(self):
        print 'hiding, standard melee'
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        ev = AddStandardMeleeAttackOrderEvent(self.sel_obj, self.obj)
        queue.put(ev)

    def add_concentration_item(self, data, menu_item_number):
        conc_data = self.sel_obj.concentration_data
        source = conc_data[0]
        data['section'][1][menu_item_number] = {}
        data['section'][1][menu_item_number]['string'] = 'Concentration (' + source['spell_name'] +')'
        data['section'][1][menu_item_number]['function'] = self.add_concentration_order
#        data['section'][1][menu_item_number]['function_args'] = (conc_data)

    def add_concentration_order(self):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        conc_data = self.sel_obj.concentration_data
        source = conc_data[0]
        func_str = conc_data[1]
        extra = conc_data[2:]
        extra.append(self.game)
        this_class = None
        if 'spell_name' in source:
            this_class = self.game.complete_dict_of_spells[source['spell_name']]
        if this_class:
            func = getattr(this_class, func_str)
            if hasattr(func, '__call__'):
                func(source,extra)
        
                        
    def add_cast_spell_menu_item(self, data, menu_item_number):
        data['section'][1][menu_item_number] = {}
        data['section'][1][menu_item_number]['string'] = 'Cast Spell   >>'
        data['section'][1][menu_item_number]['submenu_function'] = self.add_spell_submenu

    def add_spell_submenu(self, raiseme, ypos = 0):
        data = {}
        data['default'] = {}
        data['default']['font'] = self.def_font
#        data['title'] = {}
#        data['title']['string'] = 'title2 here'
        
        data['section'] = {}
        data['section']['divider'] = {}
        data['section'][1] = {}
        spell_num = 1
        for advclass, spell_list in self.sel_obj.spells_memorized.iteritems():
            for spell_name in spell_list:
#        for spell_name in self.sel_obj.spells_memorized:
                spell = self.game.complete_dict_of_spells[spell_name]
                if spell.basic_allowed_to_cast(self.sel_obj, advclass, self.game):   
                    data['section'][1][spell_num] = {}
                    data['section'][1][spell_num]['string'] = spell_name + ' as ' + advclass
    #                data['section'][1][spell_num]['font'] = fontfbtr26
                    data['section'][1][spell_num]['function'] = spell.selected
                    data['section'][1][spell_num]['function_args'] = (self.sel_obj, advclass, self.game)
                    spell_num += 1  

        if spell_num == 1:
            data['section'][1][spell_num] = {}
            data['section'][1][spell_num]['string'] = 'None'
        
        self.submenu_handling(data, raiseme, ypos)
        print 'add spell menu', data
        
    def add_pickup_menu_item(self, data, menu_item_number):
        data['section'][1][menu_item_number] = {}
        data['section'][1][menu_item_number]['string'] = 'Pick Up Item  >>'
        data['section'][1][menu_item_number]['submenu_function'] = self.add_pickup_submenu

    def add_pickup_submenu(self, raiseme, ypos = 0):
        data = {}
        data['default'] = {}
        data['default']['font'] = self.def_font
#        data['title'] = {}
#        data['title']['string'] = 'title2 here'
        
        data['section'] = {}
        data['section']['divider'] = {}
        data['section'][1] = {}
        item_num = 1
        for item_spr in self.view.hover_sprite_dict['carried_item']:
            item = item_spr.object
            data['section'][1][item_num] = {}
            data['section'][1][item_num]['string'] = item.name
            data['section'][1][item_num]['function'] = self.order_pickup_item
            data['section'][1][item_num]['function_args'] = (self.sel_obj, item)
            
            # todo - implement this function
#            data['section'][1][item_num]['function_args'] = (self.sel_obj, self.obj, self.game)
            item_num += 1

        self.submenu_handling(data, raiseme, ypos)
        print 'add pickup menu', data
        
    def submenu_handling(self, data, raiseme, ypos):        
        if raiseme:
            print 'submenu handling', data
            pos1_info = (0,ypos)
            pos2_info = self.view.mapViewPortRect
            pos3_info = self.view.primary_floating_menu_rect
            pos_info = (pos1_info, pos2_info, pos3_info)
            sfm = self.pguctrl.create_secondary_floating_menu(data, pos_info)
            self.view.secondary_floating_menu_rect = sfm.rect
            
        else:
            self.pguctrl.hide_secondary_floating_menu()
            self.view.secondary_floating_menu_rect = None
        
    def show_menu(self, data, clickpos):
        if self.view.popup_floating_rect:
            self.pguctrl.hide_primary_floating_menu()
            self.view.popup_floating_rect = None
#            ev = HideHoverPopupEvent()
#            queue.put(ev)
        pfm = self.pguctrl.create_primary_floating_menu(data, (clickpos, self.view.mapViewPortRect), background = (0,0,180,100))
        self.view.primary_floating_menu_rect = pfm.rect
        
    def eval_carried_item_right_click(self, clickpos):
        # not used, and may not be necessary since a right click on selected char always
        # brings up char right click menus, even if char standing on object
        on_tile = False
#        standard_act_avail = False 
        move_act_avail = False 
        data = deepcopy(self.default_data)
        data['default']['font'] = self.def_font
        
        self.num_menu_items += 1
        data['section'][1][self.num_menu_items] = {}
        data['section'][1][self.num_menu_items]['string'] = 'Information'
        data['section'][1][self.num_menu_items]['function'] = self.show_object_info

        if self.sel_obj:
#            self.sel_obj = sel_sp.object
            if self.sel_obj.objtype == 'playerchar': 
                if self.obj.pos == self.sel_obj.pos:
                    on_tile = True
    
#                if 'standard' not in self.sel_obj.actions_used \
#                and 'partial_standard' not in self.sel_obj.actions_used \
#                and 'full' not in self.sel_obj.actions_used:
#                    standard_act_avail = True 
                if 'move' not in self.sel_obj.actions_used \
                and 'partial_move' not in self.sel_obj.actions_used \
                and 'full' not in self.sel_obj.actions_used:
                    move_act_avail = True 
                    
#                if on_tile and standard_act_avail:            
                if on_tile and move_act_avail:            
                    self.num_menu_items += 1
                    data['section'][1][self.num_menu_items] = {}
                    data['section'][1][self.num_menu_items]['string'] = 'Pick Up'
#                    data['section'][1][self.num_menu_items]['function'] = self.show_object_info
                    
#                if self.sel_obj.spells_memorized:
#                    if standard_act_avail:
#                        self.num_menu_items += 1
#                        self.add_cast_spell_menu_item(data, self.num_menu_items)

        if self.num_menu_items == 1:
            self.show_object_info()
        else:
            self.show_menu(data, clickpos)    

    def show_terrain_info(self, mappos):
        print 'hiding, show terrain'

        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        map_section_name = self.view.viewing_map_section
        if mappos in self.game.map_data[map_section_name]['known tiles']:
            raw_data = info_popup.set_terrain_info_popup_data(map_section_name, mappos, self.game)
    #        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (50,0,150,150))
            infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (0,0,0,0))
    #        data = info_popup.set_and_format_info_popup_data(self.obj, self.sel_obj, self.game, self.view.mapViewPortRect, toppanel_height)
    #        infpw = info_popup.InfoPopup(data)
            self.view.modal_window_rect = infpw.rect
            self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
            ev = SwitchToModalControllerEvent(infpw)
            queue.put(ev)
        

    def show_inventory_screen(self):
        print 'hiding, show inventory'
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
#        raw_data = inventory_popup.set_object_inv_popup_data(self.obj, self.game)
#        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (50,0,150,150))
#        invpw = inventory_popup.InventoryScreen(self.obj, self.view.mapViewPortRect, toppanel_height, background = (150,200,150,230))
#        if self.game.move_mode == 'free':
#            allow_drag = True
#        elif self.game.move_mode == 'phased':
#            allow_drag = False
        invpw = inventory_popup.InventoryScreenWrapper(self.sel_obj, self.view.mapViewPortRect, toppanel_height, self.game.move_mode, background = (150,200,150,230))
#        data = info_popup.set_and_format_info_popup_data(self.obj, self.sel_obj, self.game, self.view.mapViewPortRect, toppanel_height)
#        infpw = info_popup.InfoPopup(data)
        self.view.modal_window_rect = invpw.rect
        self.pguctrl.show_modal_window(invpw, invpw.rect.topleft)
        ev = SwitchToModalControllerEvent(invpw)
        queue.put(ev)
        
    def show_object_info(self):
        print 'right click menus, show object info'
        
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        raw_data = info_popup.set_object_info_popup_data(self.obj, self.game, self.sel_obj)
#        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (50,0,150,150))
        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (0,0,0,0))
#        data = info_popup.set_and_format_info_popup_data(self.obj, self.sel_obj, self.game, self.view.mapViewPortRect, toppanel_height)
#        infpw = info_popup.InfoPopup(data)
        self.view.modal_window_rect = infpw.rect
        self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
        ev = SwitchToModalControllerEvent(infpw)
        queue.put(ev)
        
#        infpw = self.pguctrl.create_object_info_popup(data)
                    
    def printsomething(self):
        print 'clicked self'
        
    def submenu_test(self, raiseme, ypos = 0):
        data = {}
        data['default'] = {}
        data['default']['font'] = fontfbtr26
        data['title'] = {}
        data['title']['string'] = 'title2 here'
        
        data['section'] = {}
        data['section']['divider'] = {}
        data['section'][1] = {}   
        data['section'][1][1] = {}
        data['section'][1][1]['string'] = 'item 4'
        data['section'][1][1]['font'] = fontfbtr26
        data['section'][1][1]['function'] = self.printsomething   
        data['section'][1][2] = {}
        data['section'][1][2]['string'] = 'item 5'
        data['section'][1][2]['function'] = self.printsomething   
        
        if raiseme:
            pos1_info = (0,ypos)
            pos2_info = self.view.mapViewPortRect
            pos3_info = self.view.primary_floating_menu_rect
            pos_info = (pos1_info, pos2_info, pos3_info)
            sfm = self.pguctrl.create_secondary_floating_menu(data, pos_info)
            self.view.secondary_floating_menu_rect = sfm.rect
            
        else:
            self.pguctrl.hide_secondary_floating_menu()
            self.view.secondary_floating_menu_rect = None

    def inventory_screen_right_click(self, inv_cont, pos):
        data = deepcopy(self.default_data)
        data['default']['font'] = self.def_font
        self.num_menu_items += 1
        data['section'][1][self.num_menu_items] = {}
        data['section'][1][self.num_menu_items]['string'] = 'Extended Information'
        data['section'][1][self.num_menu_items]['function'] = self.show_extended_object_info
        data['section'][1][self.num_menu_items]['function_args'] = (inv_cont.item, inv_cont.i_s.obj,'inv_screen')
        
        if self.sel_obj.can_drop_item(inv_cont.item, self.game):
            self.num_menu_items += 1
            data['section'][1][self.num_menu_items] = {}
            data['section'][1][self.num_menu_items]['string'] = 'Drop Item to Ground'
            data['section'][1][self.num_menu_items]['function'] = self.inv_scr_drop_item
            data['section'][1][self.num_menu_items]['function_args'] = (inv_cont.item,)

        self.show_menu(data, pos)    

    def show_extended_object_info(self, obj, owner, source = None):
        print 'hiding, show extended object info'
        
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        data = obj.set_extended_object_info(owner,self.game)
        
        raw_data = {}
        raw_data['text_panel_format'] = {'background': (50,0,150,150)}
        raw_data['text'] = {}
        raw_data['text'][0] = {}
        raw_data['text'][0]['string'] = data['long_desc']    # todo - put extended info here
        raw_data['text'][0]['color'] = (250,250,0,255)
        raw_data['text'][0]['font'] = self.def_font
        
        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
        raw_data['buttons'] = {}
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
        raw_data['buttons'][0]['function'] = 'close'
        
#        raw_data = info_popup.set_object_info_popup_data(obj, owner, self.game, extended_info = True)
#        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (50,0,150,150))
        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, background = (0,0,0,0))
#        data = info_popup.set_and_format_info_popup_data(self.obj, self.sel_obj, self.game, self.view.mapViewPortRect, toppanel_height)
#        infpw = info_popup.InfoPopup(data)

#        if source == 'inv_screen' and self.pguctrl.modal_window_showing:
#            self.pguctrl.show_secondary_modal_window(infpw, infpw.rect.topleft)
#        else:
#            self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
        self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
        self.view.modal_window_rect = infpw.rect
        ev = SwitchToModalControllerEvent(infpw)
        queue.put(ev)
        
    def inv_scr_drop_item(self, item):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        ev = OrderDropItemToGroundEvent(item, self.sel_obj)
        queue.put(ev)
        
    def order_pickup_item(self, carrier, item):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        ev = OrderPickupItemFromGroundEvent(item, carrier)
        queue.put(ev)
    
    def raise_sprite_choice_menu(self, sprite_list, next_event, clickpos):
        self.num_menu_items = 0
        obj_chosen = None
        data = deepcopy(self.default_data)
        data['default']['font'] = self.def_font
        data['title'] = {}
        data['title']['string'] = 'Choose:'
        data['section']['divider'] = {}
        
        for spr in sprite_list:
            obj = spr.object
            if obj.name:
                name_str = obj.name
            else:
                name_str = obj.type + ' ' + obj.subtype
            self.num_menu_items += 1
            data['section'][1][self.num_menu_items] = {}
            data['section'][1][self.num_menu_items]['string'] = name_str
            data['section'][1][self.num_menu_items]['function'] = self.after_right_click_choice_menu
            data['section'][1][self.num_menu_items]['function_args'] = (obj, next_event, clickpos, spr)

        self.num_menu_items += 1
        data['section'][2] = {}
        data['section'][2][1] = {}
        data['section'][2][1]['string'] = 'Terrain Info'
        data['section'][2][1]['function'] = self.after_right_click_choice_menu
        data['section'][2][1]['function_args'] = (None, TerrainRightClickEvent, clickpos, None)
            
        self.show_menu(data, clickpos) 
        
    def after_right_click_choice_menu(self, obj, next_event, clickpos, clicked_sprite):
        print 'hiding, after right click'

        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        if next_event.__name__ == 'TargetChosenEvent':
            ev = next_event(obj)
            queue.put(ev)
        elif next_event.__name__ == 'SpriteRightClickEvent':
            if clicked_sprite.type == 'playerchar':
                char = clicked_sprite.object
                if self.game.myprofname == self.game.charsplayer[char.name]:
                    ev = SpriteSelectedEvent(clicked_sprite, True)
                    queue.put(ev)
                if not (self.game.move_mode == 'phased' and char.before_order_decisions):
                    ev = next_event(clicked_sprite, clickpos)
                    queue.put(ev)
            else:
                ev = next_event(clicked_sprite, clickpos)
                queue.put(ev)
        elif next_event.__name__ == 'TerrainRightClickEvent':
            mappos = self.view.convertWholeViewPortPixToMapPos(clickpos)            
            ev = TerrainRightClickEvent(mappos)
            queue.put(ev)
            
#        elif next_event.__name__ == 'SpriteSelectedEvent':
#            ev = next_event(clicked_sprite)
#            queue.put(ev)
#            if obj.objtype == 'playerchar':
#                sel_spr = clicked_sprite
#            else:
#                sel_spr = None
#            ev = SpriteRightClickEvent(clicked_sprite, clickpos, sel_spr)
            
                
    def Notify(self, event):
        if isinstance( event, SpriteRightClickEvent ):
            self.num_menu_items = 0
            self.initial_right_click_processing(event.clicked_sprite, event.clickpos)

        elif isinstance( event, PassGameRefEvent ):
            self.game = event.game
            
        elif isinstance( event, HidePrimaryFloatingMenuEvent ):
            print '***********rcm, hiding from event'
            self.pguctrl.hide_primary_floating_menu()
            self.view.primary_floating_menu_rect = None
            
        elif isinstance( event, HideSecondaryFloatingMenuEvent ):
            self.pguctrl.hide_secondary_floating_menu()
            self.view.secondary_floating_menu_rect = None
            
        elif isinstance( event, HideHoverPopupEvent ):
            self.pguctrl.hide_primary_floating_menu()
            self.view.popup_floating_rect = None

        elif isinstance( event, InventoryScreenRightClickEvent ):
            self.num_menu_items = 0
            self.inventory_screen_right_click(event.inv_cont, event.whole_vp_pos)
            
        elif isinstance( event, RaiseSpriteChoiceMenuEvent ):
            self.raise_sprite_choice_menu(event.choice_list, event.next_event, event.clickpos)
                        
        elif isinstance( event, TerrainRightClickEvent ):
            self.show_terrain_info(event.mappos)

