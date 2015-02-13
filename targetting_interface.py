
from events import *
from fontdefs import *
from gamefunctions import * 
from copy import deepcopy
import info_popup, inventory_popup
import pygame
from pgu import gui


class TargettingInterface():
    def __init__(self, evManager, uv):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
    
        self.uv = uv
        self.view = self.uv.view
        self.pguctrl = self.uv.pguctrl
        
        self.source = None
        self.source_obj = None
        self.target_obj = None
        self.find_all_valid_targets_func = None
        self.target_chosen_func = None
        self.cancel_func = None
        self.area_effect_func = None

    def cancel_targeting(self):
        self.pguctrl.hide_nonmodal_popup()
        self.view.nonmodal_popup_rect = None
#        self.view.set_allowed_tiles_and_targets(set(), set())
        if self.source_obj:
            self.source_obj.allowed_target_locs = set()
            self.source_obj.allowed_targets = set()
            ev = SetSelectionToObject(self.source_obj)
            self.view.uv.set_selection_to_object(ev)
#            queue.put(ev)
#            self.source_obj.find_allowed_moves_for_mobj(self.game, 'last_ordered')
#            self.view.set_allowed_tiles_and_targets(self.source_obj.allowed_move_tiles, set())
        self.source = None
        self.source_obj = None
        self.target_obj = None
        self.find_all_valid_targets_func = None
        self.target_chosen_func = None
        self.cancel_func = None
        self.area_effect_func = None
        self.view.set_effect_area_func(None)
        self.view.set_effect_area_tiles(None)
#        ev = SwitchToMainMapControllerEvent()
        self.view.mastercontroller.switch_to_main_map_controller()
#        queue.put(ev)
        self.view.updateMap(True,True)
#        ev = UpdateMap()
#        queue.put(ev)
        
#    def validate_target(self, sprite):
#        allowed = False
#        if hasattr(sprite,'object'):
#            spr_obj = sprite.object
#            if spr_obj.objtype == 'playerchar' or spr_obj.objtype == 'monster':
#                self.target = spr_obj
#                allowed = self.validate_target_func(self.caster, spr_obj, self.game)
#        return allowed
    
    def set_valid_targets(self):
        self.allowed_tiles, self.allowed_targets = self.find_all_valid_targets_func(self.source,self.game)
        print '$$$$$$$$$$$ targetting interface, valid targets $$$$$$$$$$$$$'
        self.source_obj.allowed_target_locs = self.allowed_tiles
        self.source_obj.allowed_targets = self.allowed_targets
#        self.view.set_allowed_tiles_and_targets(self.allowed_tiles, self.allowed_targets)

#        self.view.set_allowed_tiles_overlay(self.allowed_tiles)
#        self.view.set_allowed_target_sprites(self.allowed_targets)

    def show_target_interface(self, event):
        problem_with_targetting = False
        self.source = event.source
        if hasattr(event.find_all_valid_targets_func,'__call__'):
            self.find_all_valid_targets_func = event.find_all_valid_targets_func
        else:
            problem_with_targetting = True
        if hasattr(event.chosen_func,'__call__'):
            self.target_chosen_func = event.chosen_func
        else:
            problem_with_targetting = True
        if hasattr(event.cancel_func,'__call__'):
            self.cancel_func = event.cancel_func
        else:
            problem_with_targetting = True
        if 'obj_id' in self.source:
            if self.source['obj_id'] in self.game.objectIdDict:
                self.source_obj = self.game.objectIdDict[self.source['obj_id']]
            else:
                problem_with_targetting = True
        else:
            problem_with_targetting = True
        if event.area_effect_func:
            if hasattr(event.area_effect_func,'__call__'):
                self.area_effect_func = event.area_effect_func
            
        if not problem_with_targetting:
            self.set_valid_targets()
            if not self.allowed_tiles and not self.allowed_targets:
                msg = 'No valid targets'
            else:
                msg = event.msg
            self.view.set_effect_area_func(self.area_effect_func)
            raw_data = info_popup.set_choose_target_popup_data(msg, self.cancel_func)
            infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, draggable = True, background = (0,0,0,0))
            self.view.nonmodal_popup_rect = infpw.rect
            if self.pguctrl.nonmodal_popup_showing:
                self.pguctrl.hide_nonmodal_popup()
            self.pguctrl.show_nonmodal_popup(infpw, infpw.rect.topleft)
            ev = SwitchToTargetingControllerEvent(infpw, self.cancel_func)
            self.view.mastercontroller.switch_to_targeting_controller(ev)
            self.view.updateMap(True,True)
        else:
            msg = 'Problem with Targetting'
            if 'attack_type' in self.source:
                msg += ' for ' + self.source['attack_type'] 
            if 'spell_name' in self.source:
                msg += ' for ' + self.source['spell_name'] 
            if 'obj_id' in self.source:
                obj = self.game.objectIdDict[self.source['obj_id']]
                msg += ' from ' + obj.name
            ev = ShowDefaultInfoPopupEvent(msg)
            queue.put(ev)
        
        
    def Notify(self, event):
        if isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, TargetChosenEvent ):
            # event.target may be either an object or a mappos.  target_chosen_func
            # determines how to use event.target
            if event.target in self.allowed_targets or event.target in self.allowed_tiles:  
                self.target_chosen_func(self.source_obj, event.target, self.game)
            
        elif isinstance( event, ShowChooseTargetInterfaceEvent ):
            self.show_target_interface(event)
            
        elif isinstance( event, ClearTargetInterfaceEvent ):
            self.cancel_targeting()
