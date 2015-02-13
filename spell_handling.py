
from events import *
from fontdefs import *
from gamefunctions import * 
from copy import deepcopy
import info_popup, inventory_popup
import pygame
from pgu import gui


class SpellHandling():
    def __init__(self, evManager, uv):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
    
        self.uv = uv
        self.view = self.uv.view
        self.pguctrl = self.uv.pguctrl
        
        self.caster = None
        self.validate_target_func = None
        self.target_chosen_func = None
        self.target = None

    def cancel_targeting(self):
        self.pguctrl.hide_nonmodal_popup()
        self.view.nonmodal_popup_rect = None
        self.caster = None
        self.target = None
        self.validate_target_func = None
        self.target_chosen_func = None
        ev = SwitchToMainMapControllerEvent()
        queue.put(ev)
        
    def validate_target(self, sprite):
        allowed = False
        if hasattr(sprite,'object'):
            spr_obj = sprite.object
            if spr_obj.objtype == 'playerchar' or spr_obj.objtype == 'monster':
                self.target = spr_obj
                allowed = self.validate_target_func(self.caster, spr_obj, self.game)
        return allowed

    def Notify(self, event):
        if isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, SpriteRightClickTargetEvent ):
            if hasattr(self.validate_target_func, '__call__'):  # to test if funcs are callable
                if self.validate_target(event.clicked_sprite):
                    if hasattr(self.target_chosen_func, '__call__'):
                        self.target_chosen_func(self.caster, self.target)
            
        elif isinstance( event, ShowChooseTargetInterfaceEvent ):
            self.caster = event.source
            self.validate_target_func = event.validate_func
            self.target_chosen_func = event.chosen_func
            raw_data = info_popup.set_choose_target_popup_data(event.msg, self.cancel_targeting, show_cancel = event.show_cancel)
            infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.view.mapViewPortRect, toppanel_height, draggable = True, background = (0,0,0,0))
            self.view.nonmodal_popup_rect = infpw.rect
            if self.pguctrl.nonmodal_popup_showing:
                self.pguctrl.hide_nonmodal_popup()
            self.pguctrl.show_nonmodal_popup(infpw, infpw.rect.topleft)
            ev = SwitchToTargetingControllerEvent(infpw)
            queue.put(ev)
            
        elif isinstance( event, ClearTargetInterfaceEvent ):
            self.cancel_targeting()
