import Queue
#import copy

import pygame
from pygame.locals import *

#from math import *
import math
#from random import *

#from pgu import gui

from events import *
from evmanager import *
from game import *
from gamefunctions import *
#from controllers import *
from mainview import *
#from internalconstants import *
from userconstants import *
import spritevisuals
import random
import right_click_menus as rcm
import targetting_interface

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

##class UnitModePopUp(gui.Table):
##  """..."""
##  def __init__(self,unit,**params):
##      gui.Table.__init__(self,**params)
##
##      #self.stealth = unit.stealth
##
##      g = gui.Group(value=unit.stealth)
##      #g = gui.Group(value=)
##
##      self.tr()
##      self.td(gui.Label('Stealth'),colspan = 2)
##      self.tr()
##      self.td(gui.Label('Low'))
##      self.td(gui.Radio(g, 0))
##      self.tr()
##      self.td(gui.Label('Med'))
##      self.td(gui.Radio(g,1))
##      self.tr()
##      self.td(gui.Label('High'))
##      self.td(gui.Radio(g,2))
##
##      g.connect(gui.CHANGE, ChangeStealth, (g, unit))

'''class UnitModePopUp(gui.Table):
    """..."""
    def __init__(self,unit,**params):
        gui.Table.__init__(self,**params)

        #self.stealth = unit.stealth

        self.g = gui.Group(value=unit.stealth)
        #g = gui.Group(value=)

        self.tr()
        self.td(gui.Label('Stealth'),colspan = 2)
        self.tr()
        self.td(gui.Label('Low'))
        self.td(gui.Radio(self.g, 0))
        self.tr()
        self.td(gui.Label('Med'))
        self.td(gui.Radio(self.g,1))
        self.tr()
        self.td(gui.Label('High'))
        self.td(gui.Radio(self.g,2))'''

        #g.connect(gui.CHANGE, ChangeStealth, (g, unit))

##def ChangeStealth(arg):
##  g,unit = arg
##  unit.stealth = g.value

#----------------------------------------------------------------------
class UnitView:
    '''...'''
    def __init__(self, evManager, view, pguctrl):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

        self.view = view
        self.pguctrl = pguctrl

        self.right_click_menu_class = rcm.RightClickMenus(evManager, self)
        self.targetting_interface_class = targetting_interface.TargettingInterface(evManager, self)
        
        self.view.transferUVref(self)
        ev = PassUnitViewRef(self)
        queue.put(ev)


        #self.spritedata = {}
        
    def sendControllerRefToUv(self, controllerref):
        self.mastercontroller = controllerref

    def transfer_SV_ref(self, svref):
        self.SV = svref
    #----------------------------------------------------------------------

    def AssembleOrderLineSprite(self, color, startpos, endpos, sp):

        new_sprites = spritevisuals.drawLineSeg(self.view, startpos, endpos, color, self.view.orderlineslayer)
        
        for line_sprite in new_sprites:
            sp.order_lines.append(line_sprite)
        
#        vsstartpos = self.view.convertMapPosToViewSurfPos(startpos)
#        vsendpos = self.view.convertMapPosToViewSurfPos(endpos)
#        
#        splitlinex = False
#        splitliney = False
#        if wrap_East_West:
#            if startpos[0] - endpos[0] > 1:
#                splitlinex = True
#                vse1x = self.view.convertMapPosToTLViewSurfPos((startpos[0]+1,startpos[1]))[0] - 1
#                                                                    # gives right edge
#                                                                    # of start tile
#                vss2x = self.view.convertMapPosToTLViewSurfPos(endpos)[0]     # gives left edge
#                                                                    # of end tile
#                
#            elif endpos[0] - startpos[0] > 1:
#                splitlinex = True
#                vse1x = self.view.convertMapPosToTLViewSurfPos(startpos)[0]   # gives left edge
#                                                                    # of start tile
#                vss2x = self.view.convertMapPosToTLViewSurfPos((endpos[0]+1,endpos[1]))[0] - 1
#                                                                    # gives right edge
#                                                                    # of end tile
#
#        if wrap_North_South:
#            if startpos[1] - endpos[1] > 1:
#                splitliney = True
#                vse1y = self.view.convertMapPosToTLViewSurfPos((startpos[0],startpos[1]+1))[1] - 1
#                                                                    # gives bottom edge
#                                                                    # of start tile
#                vss2y = self.view.convertMapPosToTLViewSurfPos(endpos)[1]     # gives top edge
#                                                                    # of end tile
#                
#            elif endpos[1] - startpos[1] > 1:
#                splitliney = True
#                vse1y = self.view.convertMapPosToTLViewSurfPos(startpos)[1]   # gives top edge
#                                                                    # of start tile
#                vss2y = self.view.convertMapPosToTLViewSurfPos((endpos[0],endpos[1]+1))[1] - 1
#                                                                    # gives bottom edge
#                                                                    # of end tile
#            
#        if splitlinex and not splitliney:
#            vse1y = (vsstartpos[1] + vsendpos[1]) / 2
#            vss2y = vse1y
#        elif splitliney and not splitlinex:
#            vse1x = (vsstartpos[0] + vsendpos[0]) / 2
#            vss2x = vse1x
            
#        if splitlinex or splitliney:
#            newSprite = spritevisuals.createLineSprite(color, vsstartpos, es1pos)
#            newSprite._layer = self.view.orderlineslayer   
#            self.view.allMapSprites.add(newSprite)
#            
#            newSprite = spritevisuals.createLineSprite(color, ss2pos, vsendpos)
#            newSprite._layer = self.view.orderlineslayer   
#            self.view.allMapSprites.add(newSprite)
#            
#        else:
#            newSprite = spritevisuals.createLineSprite(color, vsstartpos, vsendpos)
#            newSprite._layer = self.view.orderlineslayer   
#            self.view.allMapSprites.add(newSprite)
        

    def AssembleTurnSprite(self, color, pos, num):

        basicimage = self.SV.turnSpriteDict[color, num].image

        unitSurf = pygame.Surface( (24,24), pygame.SRCALPHA )
        unitSurf.fill( (0,0,0,0) )

        unitSurf.blit(basicimage, (0,0))
        unitSurf = unitSurf.convert_alpha(self.view.viewedTerrain)

        newSprite = pygame.sprite.Sprite()

        newSprite.rect  = unitSurf.get_rect()
        newSprite.image = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        newSprite.rect.center = self.view.convertMapPosToViewSurfPos(pos)
        newSprite._layer = self.view.orderspriteslayer        
        self.view.allMapSprites.add(newSprite)
        
    def AssembleAllowedMoveSprite(self, pos):

        basicimage = self.SV.allowed_move_sprite.image

        unitSurf = pygame.Surface( (tilepixsize,tilepixsize), pygame.SRCALPHA )
        unitSurf.fill( (0,0,0,0) )

        unitSurf.blit(basicimage, (0,0))
        unitSurf = unitSurf.convert_alpha(self.view.viewedTerrain)

        newSprite = pygame.sprite.Sprite()

        newSprite.rect  = unitSurf.get_rect()
        newSprite.image = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        newSprite.rect.center = self.view.convertMapPosToViewSurfPos(pos)
        newSprite._layer = self.view.allowed_move_layer
        newSprite.type = 'allowed_move'
        return newSprite        
#        self.view.allMapSprites.add(newSprite)
        
    def AssembleOrderSprite(self, modechange, color, pos):

        basicimage = self.SV.orderSpriteDict[modechange, color].image

        unitSurf = pygame.Surface( (24,24), pygame.SRCALPHA )
        unitSurf.fill( (0,0,0,0) )

        unitSurf.blit(basicimage, (0,0))
        unitSurf = unitSurf.convert_alpha(self.view.viewedTerrain)

        newSprite = pygame.sprite.Sprite()

        newSprite.rect  = unitSurf.get_rect()
        newSprite.image = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        newSprite.rect.center = self.view.convertMapPosToViewSurfPos(pos)
        newSprite._layer = self.view.orderspriteslayer   
        self.view.allMapSprites.add(newSprite)

    #----------------------------------------------------------------------
    
    def AssembleSprite(self, gameobject):
        strtype = gameobject.objtype
        if strtype == "playerchar":
            layer = self.view.myspriteslayer
        elif strtype == 'monster':
            layer = self.view.otherteamvislayer
        elif strtype == 'carried_item':
            layer = self.view.carried_item_layer
            
        if strtype == "playerchar":
            basicimage = self.SV.player_tile_dict[gameobject.name]
        elif strtype == 'monster':
            basicimage = random.choice(self.SV.monster_tile_dict[gameobject.species])
        elif strtype == 'carried_item':
            if gameobject.name in self.SV.object_tile_dict:
                basicimage = random.choice(self.SV.object_tile_dict[gameobject.name])
            elif (gameobject.type, gameobject.subtype) in self.SV.object_tile_dict:
                basicimage = random.choice(self.SV.object_tile_dict[(gameobject.type, gameobject.subtype)])
            else:
                pass    # put up default sprite
        
        rect = basicimage.get_rect()
        unitSurf = pygame.Surface( rect.size, pygame.SRCALPHA )
        unitSurf.fill((0,0,0,0)) #will maintain transparency of basicsprite.image
        
        unitSurf.blit(basicimage, (0,0))
        unitSurf = unitSurf.convert_alpha(self.view.viewedTerrain)

        newSprite = pygame.sprite.Sprite()

        newSprite.rect  = unitSurf.get_rect()
        newSprite.imageus = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
#        unitSurf.blit(SV.selectionSprite.image, (0,0) )
#        newSprite.imagesel = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
#        unitSurf.blit(SV.PursuedselectionSprite.image, (0,0) )
#        newSprite.imageselPursued = unitSurf.convert_alpha(self.view.viewedTerrain)
        newSprite.image = newSprite.imageus
        newSprite.selected = 0
        newSprite.pursued = 0
        newSprite.type = strtype
        newSprite.object = gameobject
        
        self.update_sprite_image(newSprite)
        print 'unitview, assemble sprite', gameobject, gameobject.pos
        self.setSpriteLocation(newSprite, gameobject.pos)
        newSprite._layer = layer
        newSprite.default_layer = layer
        newSprite.order_lines = []
        newSprite.order_sprites = []
#        self.view.allMapSprites.add(newSprite)
        return newSprite
        
    
    def AssembleObjectSprite(self, gameobject):
        # only come here if sprite is visible
        
        # possible types are: "unit", "city", "group"

        if gameobject.nation == None:
            nation = "neutral"
        else:
            nation = gameobject.nation
            
        strtype = gameobject.objtype
        
        #print gameobject.team, self.game.myteam
        
        if strtype == "city":
            layer = self.view.citylayer
        elif strtype == "supply":
            layer = self.view.supplyunitlayer
        else:  
            if nation == self.game.mynation:
                layer = self.view.myspriteslayer
            elif gameobject.team == self.game.myteam:
                layer = self.view.myteam.layer
            #elif self.game.myteam in gameobject.visible_to:
                #layer = self.view.otherteamvislayer
            #else:
                #print "error in assembling object sprite"
            else:
                layer = self.view.otherteamvislayer
                
            
        
        if strtype == "city":
            basicimage = self.SV.citySpriteDict[nation]
            medimage = self.SV.medcitySpriteDict[nation]
            miniimage = self.SV.minicitySpriteDict[nation]
        elif strtype == "unit":
            type = gameobject.subtype
            if type == "Supply":
                basicimage = self.SV.supplySpriteDict[nation]
                medimage = self.SV.medsupplySpriteDict[nation]
                miniimage = self.SV.minisupplySpriteDict[nation]
            else:
                basicimage = self.SV.unitSpriteDict[nation][type]
                medimage = self.SV.unitMedSpriteDict[nation][type]
                miniimage = self.SV.unitMiniSpriteDict[nation][type]
        elif strtype == "unitgroup":
            num = gameobject.groupnumber
            basicimage = self.SV.unitGroupSpriteDict[nation][num]
            medimage = self.SV.unitGroupMedSpriteDict[nation][num]
            miniimage = self.SV.unitGroupMiniSpriteDict[nation][num]
        #color = self.game.Nations[nation].color

        #unitposx = unit.pos[0]
        #unitposy = unit.pos[1]

        unitSurf = pygame.Surface( basicimage.rect.size, pygame.SRCALPHA )
        #unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0)) #will maintain transparency of basicsprite.image
        
        #print "afterconvert", unitSurf.get_at( (3,3) )

        unitSurf.blit(basicimage.image, (0,0))
        #print "afterblit", unitSurf.get_at( (3,3) )
        unitSurf = unitSurf.convert_alpha(self.view.viewedTerrain)

        #if spritedata['selected']:
        #   unitSurf.blit(self.selectionSprite.image, (0,0))

#       unitSurf.set_colorkey((0,1,0))

        #newSprite = pygame.sprite.Sprite(spritedata['group'])
        #newSprite = pygame.sprite.Sprite(self.view.allMapSprites)
        newSprite = pygame.sprite.Sprite()

        newSprite.rect  = unitSurf.get_rect()
        newSprite.imageus = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        unitSurf.blit(self.SV.selectionSprite.image, (0,0) )
        newSprite.imagesel = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        unitSurf.blit(self.SV.PursuedselectionSprite.image, (0,0) )
        newSprite.imageselPursued = unitSurf.convert_alpha(self.view.viewedTerrain)
        newSprite.image = newSprite.imageus
        newSprite.selected = 0
        newSprite.pursued = 0
        newSprite.type = strtype
        newSprite.object = gameobject
        
        self.setSpriteLocation(newSprite, gameobject.pos)
        newSprite._layer = layer
        self.view.allMapSprites.add(newSprite)
        
        
        
        #basicsprite = self.unitMiniSpriteDict[nation][type]
        unitSurf = pygame.Surface( miniimage.rect.size )
        unitSurf.blit(miniimage.image, (0,0))
        newSprite2 = pygame.sprite.Sprite()

        newSprite2.rect  = unitSurf.get_rect()
        newSprite2.image = unitSurf
        newSprite2.rect.center = self.view.convertMapPosToMiniMapPos(gameobject.pos)
        newSprite2._layer = layer
        #newSprite2.normallayer = layer
        newSprite.minisprite = newSprite2
        self.view.allMiniMapSprites.add(newSprite2)
        
        #basicsprite = self.unitMedSpriteDict[nation][type]
#        unitSurf = pygame.Surface( medimage.rect.size, pygame.SRCALPHA )
#        unitSurf.fill((0,0,0,0))
#        unitSurf.blit(medimage.image, (0,0))
#        unitSurf = unitSurf.convert_alpha(self.view.selectionWindow)
#        newSprite3 = pygame.sprite.Sprite()
#
#        newSprite3.rect  = unitSurf.get_rect()
#        newSprite3.imageus = unitSurf.copy().convert_alpha(self.view.selectionWindow)
#        unitSurf.blit(self.medselectionSprite.image, (0,0) )
#        newSprite3.imagesel = unitSurf.convert_alpha(self.view.viewableMap[0])
#        newSprite3.image = newSprite3.imageus
#        newSprite3.selected = 0
        
        medsprite = self.AssembleMedSprite(gameobject)
        
#        medsprite.mainsprite = newSprite
        newSprite.medsprite = medsprite
        
#        if strtype == 'unitgroup':
#            newSprite.groupsprites = []
                

        #if self.game.myteam == unit.team:
            #self.AssembleViewCircleSprite(unit, newSprite)

        

        #newSprite.color = color

        #xpos = int(round(unitposx / self.view.hor_conv))
        #ypos = int(round(unitposy / self.view.ver_conv))
        #newSprite.minimap_pos = (xpos,ypos)
        #newSprite.minimap_pos = self.view.convertMapPosToMiniMapPos(unit.pos)

        return newSprite

    def AssembleMedSprite(self, gameobject):
        
        if gameobject.nation == None:
            nation = "neutral"
        else:
            nation = gameobject.nation
            
        strtype = gameobject.objtype
        
        if strtype == "city":
            medimage = self.SV.medcitySpriteDict[nation]
        elif strtype == "unit":
            type = gameobject.subtype
            if type == "Supply":
                medimage = self.SV.medsupplySpriteDict[nation]
            else:
                medimage = self.SV.unitMedSpriteDict[nation][type]
        elif strtype == "unitgroup":
            num = gameobject.groupnumber
            medimage = self.SV.unitGroupMedSpriteDict[nation][num]
        
        unitSurf = pygame.Surface( medimage.rect.size, pygame.SRCALPHA )
        unitSurf.fill((0,0,0,0))
        unitSurf.blit(medimage.image, (0,0))
        unitSurf = unitSurf.convert_alpha(self.view.selectionWindow)
        newSprite3 = pygame.sprite.Sprite()

        newSprite3.rect  = unitSurf.get_rect()
        newSprite3.imageus = unitSurf.copy().convert_alpha(self.view.selectionWindow)
        unitSurf.blit(self.SV.medselectionSprite.image, (0,0) )
        newSprite3.imagesel = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        unitSurf.blit(self.SV.PursuedmedselectionSprite.image, (0,0) )
        newSprite3.imageselPursued = unitSurf.convert_alpha(self.view.viewedTerrain)
        newSprite3.image = newSprite3.imageus
        newSprite3.selected = 0
        newSprite3.object = gameobject
        #newSprite3.mainsprite = newSprite
        #newSprite.medsprite = newSprite3
        
        #if strtype == 'unitgroup':
            #newSprite.groupsprites = []
                
        return newSprite3
        

    #----------------------------------------------------------------------
    
    def RotateSupplySprite(self, obj):
        rotangle = 0
        if obj.orders:
            firstord = obj.orders[0]
            if firstord[0] == 'move' and firstord[1]:
                currentdest = firstord[1][0]
                deltax = currentdest[0] - obj.pos[0]
                deltay = currentdest[1] - obj.pos[1]
                if deltax != 0:
                    rotangle = math.pi/2 - math.atan(float(deltay)/deltax)
                    
        return rotangle*180/math.pi
            
    def show_sprite_of_object(self, object, updatemap = True, group = None):

        objectSprite = self.GetObjectSprite(object, group)
        
#        print 'in uv, showsprite', object.id
        
        if objectSprite == None:
            objectSprite = self.AssembleSprite(object)
            group.append(objectSprite)
        else:
            self.update_sprite_image(objectSprite)
            self.setSpriteLocation(objectSprite, object.pos)
#            objectSprite.minisprite.rect.center = self.view.convertMapPosToMiniMapPos(object.pos)
            
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
        return objectSprite
            
    def hide_sprite_of_object(self, object, updatemap = True):
        
        objectSprite = self.GetObjectSprite(object, self.view.allMapSprites)
        self.view.allMapSprites.remove(objectSprite)
        self.view.allMiniMapSprites.remove(objectSprite.minisprite)
        del objectSprite
        
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
            
    def refreshAllVisSprites(self):
        
#        self.view.allMapSprites.empty()
        self.view.party_sprites = []
        self.view.monster_sprites = []
        self.view.object_sprites = []
#        self.view.allMiniMapSprites.empty()

        selected_id = None
        if self.view.selectedSprite:
            if hasattr(self.view.selectedSprite,'object'):
                if self.view.selectedSprite.type == 'playerchar':
                    selected_id = self.view.selectedSprite.object.id
        for o in self.game.objectIdDict.itervalues():
#            if o.alive:
            if o.objtype == 'playerchar':
                self.show_sprite_of_object(o,updatemap = False, group = self.view.party_sprites)
            elif o.objtype == 'monster':
                self.show_sprite_of_object(o,updatemap = False, group = self.view.monster_sprites)
            elif o.objtype == 'carried_item' and not o.carried:
                self.show_sprite_of_object(o,updatemap = False, group = self.view.object_sprites)

        if selected_id:
            selected_obj = self.game.objectIdDict[selected_id]
#            object_sprite = self.GetObjectSprite(selected_obj, self.view.allMapSprites)
            object_sprite = self.GetObjectSprite(selected_obj, self.view.party_sprites)
            self.setSelectionToSprite(object_sprite, False)

                                
#                if o.team == team:
#                    self.show_sprite_of_object(o,False)
#                elif team in o.visible_to:
#                    self.show_sprite_of_object(o,False)
#            elif o.objtype == 'unitgroup' and o.team == team:
#                self.show_sprite_of_object(o,False)
                    
        self.showOrders()                    
        eV = UpdateMap(True)
        queue.put(eV)
                
                


##  #----------------------------------------------------------------------
##  def MoveUnit(self, unit):
##      self.spritedata.clear()
##
##      unitSprite = self.GetUnitSprite(unit)
##      if unitSprite:
##              self.view.myUnitSprites.remove(unitSprite)
##
##      self.spritedata['selected']=True
##
##      unitSprite = AssembleUnitSprite(unit, self.spritedata)
##
##      self.view.myUnitSprites.add(unitSprite)
##
##      ev = UpdateMap()
##      self.evManager.Post( ev )

    #----------------------------------------------------------------------
    def GetObjectSprite(self, object, group):
        retval = None
        if group:
            for s in group:
                if hasattr(s,'object') and s.object == object:
                    retval = s
                    break
        return retval

    #----------------------------------------------------------------------
    #def SpriteIsVisible(self, sprite):

    #   return sprite.rect.colliderect(self.mapRect)

    #----------------------------------------------------------------------
    
    def selectRectEvent(self, pos1, pos2):
        if pos1:
            vsstartpos = self.view.convertWholeViewPortPixToVSPix(pos1)
            vsendpos = self.view.convertWholeViewPortPixToVSPix(pos2)
            spritelist = self.SpritesInsideVSRect(vsstartpos, vsendpos)
    #        self.view.selectedSprites = spritelist
            self.setSelectionToSpritelist(spritelist)
    
    def SpritesInsideVSRect(self, vsstartpos, vsendpos, addTeammates = True, addEnemies = True):
        
        rectwidth = abs(vsstartpos[0]-vsendpos[0])
        rectheight = abs(vsstartpos[1]-vsendpos[1])
        rectleft = min( (vsstartpos[0],vsendpos[0]) )
        recttop = min( (vsstartpos[1],vsendpos[1]) )
        
        sR = pygame.Rect(rectleft, recttop, rectwidth, rectheight)
        spritelist = []
        for sp in self.view.allMapSprites.sprites():
            if hasattr(sp,"object"):
                if sp.rect.colliderect(sR):
                    obj = sp.object
                    if obj.nation == self.game.mynation:
                        spritelist.append(sp)                    
                    elif addTeammates and obj.team == self.game.myteam:
                        spritelist.append(sp)
                    elif addEnemies and obj.team != self.game.myteam:
                        spritelist.append(sp)
        
        return spritelist
#        setAllSelectionGraphics(True)

    def setSelectionToSprite(self, sprite, left_click):
        if self.view.selectedSprite:
            something_had_been_selected = True
#            self.clearAllSelectionGraphics(False)
            self.clearAllSelectionGraphics()
        else:
            something_had_been_selected = False
        selection_failed = True
        if sprite:
            if sprite.type == "playerchar":
                object = sprite.object
                if self.game.myprofname == self.game.charsplayer[object.name]:
                    object = sprite.object
                    if self.game.move_mode == 'phased' and object.before_order_decisions and left_click:
                        self.mastercontroller.clientresults.handle_before_order_decisions(object)
                    else:
                        selection_failed = False    
                        sprite.selected = 1
                        self.update_sprite_image(sprite)
                        sprite._layer = self.view.selectedlayer
                        
                        self.view.selectedSprite = sprite            
                            
                        if self.game.move_mode == 'phased':
                            if self.view.atmovieend:
                                ev = FindAllowedMovesEvent(object,'last_ordered')
                                queue.put(ev)
                            print 'unitview, set selection to sprite'
                            ev = SetAllowedMovesVisualsEvent(object)
                            queue.put(ev)
                            self.pguctrl.set_toppanel_action_mode(object)
                        
#        if something_had_been_selected and selection_failed:
#            ev = SetAllowedMovesVisualsEvent(None)
#            queue.put(ev)
#            self.pguctrl.set_toppanel_action_mode(None)
#            self.view.updateSelectionWindow()
#            eV = UpdateMap()
#            queue.put(eV)
        if not selection_failed:
            self.view.updateSelectionWindow()
            eV = UpdateMap()
            queue.put(eV)
            

    def SetPursuedSelectionGraphic(self, sprite, updatemap = True):
        sprite.pursued = 1
        self.update_sprite_image(sprite)
#        self.setSpriteLocation(sprite, sprite.object.pos)
#        sprite.image = sprite.imageselPursued
        if self.view.allMapSprites.get_layer_of_sprite(sprite) != self.view.selectedlayer: 
            self.view.allMapSprites.change_layer(sprite, self.view.selectedlayer)
#            self.view.allMiniMapSprites.change_layer(sprite.minisprite, self.view.selectedlayer)
        
#        if self.view.pursuedObj.type == "unit" or self.view.pursuedObj.type == "unitgroup":
#            object = self.view.pursuedObj.object

#        self.view.updateSelectedUnitsInSelectionWindow()
        
#        if self.view.puvis:
#            if self.view.pursuedObj.type == "unit" or self.view.pursuedObj.type == "unitgroup":
#                self.pguctrl.UpdateUMPChoices(object)
#                self.pguctrl.ShowUnitModePopUp()
#            else:
#                eV = UmpuVisChange()
#                queue.put(eV)
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
            


    def clearAllSelectionGraphics(self, updatemap = True):
        sS = self.view.selectedSprite 
        if sS:
            sS.selected = 0
            self.update_sprite_image(sS)
            sS._layer = sS.default_layer
            self.view.selectedSprite = None
            
            print '############### unitview clear selection #################'
            ev = SetAllowedMovesVisualsEvent(None)
            queue.put(ev)
            self.pguctrl.set_toppanel_action_mode(None)
            self.view.updateSelectionWindow()
        self.ClearPursuedSelectionGraphics(False)
        self.view.pursuedSprites = []
            
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
    
    def ClearPursuedSelectionGraphics(self, updatemap = True):
        for sp in self.view.pursuedSprites:
            sp.pursued = 0
            self.update_sprite_image(sp)
#            sp.image = sp.imageus
            if self.view.allMapSprites.get_layer_of_sprite(sp) == self.view.selectedlayer:
                self.view.allMapSprites.change_layer(sp, sp._layer)
#                self.view.allMiniMapSprites.change_layer(sp.minisprite, sp.minisprite._layer)
                
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
            
    def setSelectionToGroup(self, mgroup):
        objlist = mgroup.returnAllMemberObjects(self.game)
        spritelist = self.spritelistFromobjlist(objlist)
        self.setSelectionToSpritelist(spritelist)
    
    def SelectUnit(self, selectedSprite, updatemap = True):     # not used atm
        self.ClearSelection(False)
        self.ClearPursuedSelection(False)
        self.view.selectedObj = selectedSprite
        
        selectedSprite.selected = 1
        selectedSprite.image = selectedSprite.imagesel
        if self.view.allMapSprites.get_layer_of_sprite(selectedSprite) != self.view.selectedlayer: 
            self.view.allMapSprites.change_layer(selectedSprite, self.view.selectedlayer)
            self.view.allMiniMapSprites.change_layer(selectedSprite.minisprite, self.view.selectedlayer)
        
        if self.view.selectedObj.type == "unit" or self.view.selectedObj.type == "unitgroup":
            object = self.view.selectedObj.object
            if object.team == self.game.myteam:
                self.ConstructOrderData(object)
                
            if object.target:
                pursuedsprite = self.GetObjectSprite(object.target, self.view.allMapSprites)
                self.SelectPursuedUnit(pursuedsprite, False)
                
        self.view.updateSelectedUnitsInSelectionWindow()
        
        if self.view.puvis:
            if self.view.selectedObj.type == "unit" or self.view.selectedObj.type == "unitgroup":
                self.pguctrl.UpdateUMPChoices(object)
#                self.pguctrl.HideUnitModePopUp()
                self.pguctrl.ShowUnitModePopUp()
#                wx.CallAfter(self.view.gcpan.UpdateUMPChoices, object)
            else:
                eV = UmpuVisChange()
                queue.put(eV)

        if updatemap:
            eV = UpdateMap()
            queue.put(eV)

    def SelectPursuedUnit(self, selectedSprite, updatemap = True):
        #tmppuvis = self.view.puvis
        self.ClearPursuedSelection(False)
        self.view.pursuedObj = selectedSprite
        
        selectedSprite.pursued = 1
        selectedSprite.image = selectedSprite.imageselPursued
        if self.view.allMapSprites.get_layer_of_sprite(selectedSprite) != self.view.selectedlayer: 
            self.view.allMapSprites.change_layer(selectedSprite, self.view.selectedlayer)
            self.view.allMiniMapSprites.change_layer(selectedSprite.minisprite, self.view.selectedlayer)
        
        if self.view.pursuedObj.type == "unit" or self.view.pursuedObj.type == "unitgroup":
            object = self.view.pursuedObj.object
            #if object.team == self.game.myteam:
            #    self.ConstructOrderData(object)

        self.view.updateSelectedUnitsInSelectionWindow()
        
        if self.view.puvis:
            if self.view.pursuedObj.type == "unit" or self.view.pursuedObj.type == "unitgroup":
                self.pguctrl.UpdateUMPChoices(object)
#                self.pguctrl.HideUnitModePopUp()
                self.pguctrl.ShowUnitModePopUp()
#                wx.CallAfter(self.view.gcpan.UpdateUMPChoices, object)
            else:
                eV = UmpuVisChange()
                queue.put(eV)
        if updatemap:
            eV = UpdateMap()
            queue.put(eV)
            
    def ClearSelection(self, updatemap = True):     # not used
        sO = self.view.selectedObj
        self.view.subselectedLoc = None
        if sO:
            sO.selected = 0
            #sO.image.blit(sO.imageus, (0,0))
            sO.image = sO.imageus
            if self.view.allMapSprites.get_layer_of_sprite(sO) == self.view.selectedlayer:
                self.view.allMapSprites.change_layer(sO, sO._layer)
                self.view.allMiniMapSprites.change_layer(sO.minisprite, sO.minisprite._layer)
                
            if sO.type == "unit" or sO.type == "unitgroup":
                '''if self.view.puvis:
                    wx.CallAfter(self.view.gcpan.HideUnitModePopUp)
                    self.view.puvis = 0
                '''
                if not self.view.showallunitorders:
                    self.view.allMapSprites.remove_sprites_of_layer(self.view.orderspriteslayer)
                    self.view.allMapSprites.remove_sprites_of_layer(self.view.orderlineslayer)
                    
                self.UpdateUnitWindow()
                
                if sO.object.target:
                    self.ClearPursuedSelection(False)
                    
            self.view.selectedObj = None

                    #self.view.visOrderSprites.empty()
                    #self.view.orderLineSprites.empty()
                    #del self.view.OrderLines[:]

            if updatemap:
                eV = UpdateMap()
                queue.put(eV)

                #eV = UpdateMap()
                #self.evManager.Post( eV )
                #queue.put(eV)

    def ClearPursuedSelection(self, updatemap = True):
        sO = self.view.pursuedObj
        self.view.subselectedLoc = None
        if sO:
            sO.pursued = 0
            sO.image = sO.imageus
            if self.view.allMapSprites.get_layer_of_sprite(sO) == self.view.selectedlayer:
                self.view.allMapSprites.change_layer(sO, sO._layer)
                self.view.allMiniMapSprites.change_layer(sO.minisprite, sO.minisprite._layer)
                
            self.UpdateUnitWindow(self.view.selectedObj)
                    
            self.view.pursuedObj = None

            if updatemap:
                eV = UpdateMap()
                queue.put(eV)

    #----------------------------------------------------------------------
    def UpdateUnitWindow(self,sprite=None):
        self.view.infoWindow.blit(self.view.infoWindowBackground,(0,0))

        if sprite:
            obj = sprite.object
            nametag = self.view.medfont.render("type = " + obj.subtype, 1, (255,255,255))
            self.view.infoWindow.blit(nametag,(10,40))

    #----------------------------------------------------------------------
    def NewMoveOrder(self, object, path):
        lop = object.lastOrderedPos
#        newpath = FindPath(lop, pos)
#        newpath = aStar(self.view.elevmap,lop,pos,object.type)
        for newdest in path:
            #vslop = self.view.convertMapPosToViewSurfPos(lop)
            #vsnewpos = self.view.convertMapPosToViewSurfPos(newdest)
        #self.view.OrderLines.append( (gcGreen, unit.lastOrderedPos, pos) )
        
            self.AssembleOrderLineSprite(gcGreen,lop,newdest)
            #newsprite = self.AssembleOrderLineSprite(gcGreen,lop,newdest)
            #self.view.orderLineSprites.add(newsprite)
            #self.view.OrderLines.append( (gcGreen, vslop, vsnewpos) )
            lop = newdest
            
        object.lastOrderedPos = lop
#        object.movepath.append(newpath)

        #ordernum = len(unit.orders)

        '''newOSprite = pygame.sprite.Sprite()
        dictsprite = self.orderSpriteDict['move', 'green', ordernum]
        newOSprite.image = dictsprite.image.copy()
        newOSprite.rect = dictsprite.rect.move(0,0)
        newOSprite.rect.center = pos
        self.view.visOrderSprites.add(newOSprite)'''
        
        #print 'in newmoveorder', unit.id, unit.orders
        
        '''for o in self.game.objectIdDict.itervalues():
            if o.objtype == 'unit':
                print 'in newmove order, objectiddict', o.id, o.orders
        '''
        eV = UpdateMap()
        queue.put(eV)

#    def NewModeOrder(self, unit, stealth):
#        #self.view.OrderLines.append( (gcGreen, unit.lastOrderedPos, pos) )
#        #unit.lastOrderedPos = pos
#
#        ordernum = len(unit.orders)
#
#        dictsprite = self.SV.orderSpriteDict['status', 'green', ordernum]
#        newOSprite = pygame.sprite.Sprite()
#        newOSprite.image = dictsprite.image.copy()
#        newOSprite.rect = dictsprite.rect.move(0,0)
#        newOSprite.rect.center = unit.lastOrderedPos
#        #self.view.visOrderSprites.add(newOSprite)
#
#        '''newOSprite = pygame.sprite.Sprite()
#        dictsprite = self.orderSpriteDict['move', 'green', ordernum]
#        newOSprite.image = dictsprite.image.copy()
#        newOSprite.rect = dictsprite.rect.move(0,0)
#        newOSprite.rect.center = pos
#        self.view.visOrderSprites.add(newOSprite)'''
#
#        eV = UpdateMap()
#        queue.put(eV)

    def ConstructOrderData(self, sp):
        unit = sp.object
        lop = unit.pos
        for idx,uo in enumerate(unit.orders):
            ordtype = uo[0]
            if ordtype == 'move':
                path = uo[1]
                for newdest in path:
#                    print 'unitview, cod2', unit.id, newdest
                    self.AssembleOrderLineSprite(self.SV.ordercolors[0],lop,newdest, sp)
                    lop = newdest
            elif ordtype == 'standard_attack':
                enemy_obj = self.game.objectIdDict[uo[1]]
                enemy_pos = enemy_obj.pos 
                self.AssembleOrderLineSprite(self.SV.ordercolors[2],lop,enemy_pos, sp)

    def ShowAllOrders(self):
#        oidlist = self.game.Nations[self.game.mynation].movableObjects
#        for charid in self.game.charnamesid.values():
#            char = self.game.objectIdDict[charid]
        for sp in self.view.party_sprites:
#            char = self.game.charnameschar[charname]
#            o = self.game.objectIdDict[oid]
            sp.order_lines = []
            sp.order_sprites = []
            self.ConstructOrderData(sp)

    def showOrders(self):
#        self.view.allMapSprites.remove_sprites_of_layer(self.view.orderspriteslayer)
#        self.view.allMapSprites.remove_sprites_of_layer(self.view.orderlineslayer)
        # do I need to delete the sprites too?
        
        #self.view.visOrderSprites.empty()
        #self.view.orderLineSprites.empty()
        #del self.view.OrderLines[:]

        if self.view.showallunitorders == 1:
            self.ShowAllOrders()
        elif self.view.selectedSprite:
#            if self.view.selectionContains['mynationunits']:
#                movelist, mgroupdict, evmgroupdict, nomvgroup, puremvgroup = self.evalSpriteListForMove(self.view.selectedSprites)
#            if self.view.selectedObj.type == "unit" \
#            or self.view.selectedObj.type == "unitgroup":
#                if sp.object.team == self.game.myteam and sp.type == 'unit':
#                    self.ConstructOrderData(sp.object)
            self.view.selectedSprite.order_lines = []
            self.view.selectedSprite.order_sprites = []
            self.ConstructOrderData(self.view.selectedSprite)
                    

    #----------------------------------------------------------------------
    def update_all_object_sprite_images_and_positions(self):
        
        for sp in self.view.allMapSprites:
            if hasattr(sp,"object"):
                self.update_sprite_image(sp)
                self.setSpriteLocation(sp, sp.object.pos)
                
        self.showOrders()
 
 
    def setSupplySpriteImage(self, sp):
#        self.view.allMapSprites.remove(sp)
        
        obj = sp.object
        nation = obj.nation
        tempsp = self.SV.supplySpriteDict[nation]
        
        rotangle = self.RotateSupplySprite(obj)
        unitSurf = spritevisuals.CreateRotatedSupplyImage(tempsp.image, rotangle)
        
        sp.rect = unitSurf.get_rect()
        sp.imageus = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        unitSurf.blit(self.SV.selectionSprite.image, (0,0) )
        sp.imagesel = unitSurf.copy().convert_alpha(self.view.viewedTerrain)
        unitSurf.blit(self.SV.PursuedselectionSprite.image, (0,0) )
        sp.imageselPursued = unitSurf.convert_alpha(self.view.viewedTerrain)
        sp.image = sp.imageus

#        sp.rect.center = self.view.convertMapPosToViewSurfPos(pos)
#        self.view.allMapSprites.add(newSprite)
        
    def update_sprite_image(self, sp):
#        if sp.selected:
#            img = sp.imagesel
#        elif sp.pursued:
#            img = sp.imageselPursued
#        else:
#            img = sp.imageus
        sp.image = pygame.transform.scale(sp.imageus, self.view.spritesize[self.view.zoomlevel])
        oldpos = sp.rect.center
        sp.rect = sp.image.get_rect()
        if sp.selected:
#            pygame.draw.rect( sp.image, (255,255,255), (0,0,sp.rect.width,sp.rect.height), 1)
            pygame.draw.rect( sp.image, (255,255,255), sp.rect, 1)
        elif sp.pursued:
            pygame.draw.rect( sp.image, (255,255,0), sp.rect, 1)
#        if set_sprite_pos:
#            sp.rect.center = self.view.convertMapPosToViewSurfPos(sp.object.pos)
        sp.rect.center = oldpos
                
        
    def setSpriteLocation(self, sp, pos):

#        self.update_sprite_image(sp, False)        
        sp.rect.center = self.view.convertMapPosToViewSurfPos(pos)
        
#        sp.rect.center = self.view.convertMapPosToViewedTerrainPos(pos, True)
        '''if self.view.zoomlevel == 1:
            zoomfactor = 0.5
        elif self.view.zoomlevel == 2:
            zoomfactor = 1.0
        elif self.view.zoomlevel == 3:
            zoomfactor = 2.0
        elif self.view.zoomlevel == 4:
            zoomfactor = 4.0
            
        xpos = int(round(float(sp.unit.pos[0]*zoomfactor)))
        ypos = int(round(float(sp.unit.pos[1]*zoomfactor)))
        sp.rect.center = (xpos,ypos)'''
        
    def handleGroupCreationVisuals(self, event):    # not used
        groupjoined = event.group
        newgroupcreated = event.newgroup
        obj1 = event.obj1
        obj1absorbed = event.obj1absorbed
        obj2 = event.obj2
        obj2absorbed = event.obj2absorbed
        handleSelections = event.handleSelections
        
        if newgroupcreated:
            gsprite = self.AssembleObjectSprite(groupjoined)
            #self.setSpriteLocation(newsprite, groupjoined.pos)
            #newsprite.minisprite.rect.center = self.view.convertMapPosToMiniMapPos(groupjoined.pos)
            #self.SelectUnit(sprite, False)
            #addsprite = True
            #self.view.selectionWindowSprites.add(sprite.medsprite)
            
            # display it with new group selected on map and in selection window and on minimap
        else:
            gsprite = self.GetObjectSprite(groupjoined,self.view.allMapSprites)
            if handleSelections:
                self.view.selectionWindowSpritesUpper.remove(gsprite)
            #addsprite = False
            
        if obj1absorbed:
            sprite = self.GetObjectSprite(obj1,self.view.allMapSprites)
#            if sprite.type == 'unitgroup':
#                for sp in sprite.groupsprites:
#                    gsprite.groupsprites.append(sp)
#            else:
#                gsprite.groupsprites.append(sprite)
            self.view.allMapSprites.remove(sprite)
            self.view.allMiniMapSprites.remove(sprite.minisprite)
            if handleSelections:
                self.view.selectionWindowSpritesUpper.remove(sprite)
        
        if obj2absorbed:
            sprite = self.GetObjectSprite(obj2,self.view.allMapSprites)
#            if sprite.type == 'unitgroup':
#                for sp in sprite.groupsprites:
#                    gsprite.groupsprites.append(sp)
#            else:
#                gsprite.groupsprites.append(sprite)
            self.view.allMapSprites.remove(sprite)
            self.view.allMiniMapSprites.remove(sprite.minisprite)
            if handleSelections:
                self.view.selectionWindowSpritesUpper.remove(sprite)
        
        if handleSelections:
            self.view.selectionWindowSpritesUpper.add(gsprite)
            self.view.updateSelectionWindow()
            self.SelectUnit(gsprite, True)
        #spritelist = []
        #for sp in reversed(self.view.selectionWindowSpritesUpper.sprites()):
            #spritelist.append(sp.mainsprite)
        #spritelist.append(gsprite)
        #self.view.updateSelectionWindow(spritelist,None)
        
            # select the group on map and in selection window
            
    def handleGroupLeavingVisuals(self, event):     # not used
        unitsUngrouped = event.unitsUngrouped
        group = event.group
        groupemptied = event.groupemptied
        clickedUnit = event.clickedUnit
        selectunit = event.selectunit
        
        gsprite = self.GetObjectSprite(group,self.view.allMapSprites)
        
        for u in unitsUngrouped:
            sprite = self.show_sprite_of_object(u,False)
#            sprite = self.GetObjectSprite(u,self.view.selectionWindowSpritesLower)
#            self.view.allMapSprites.add(sprite)
            if selectunit:
                self.view.selectionWindowSpritesUpper.add(sprite)
            #self.view.selectionWindowSpritesLower.remove(sprite)
#            self.view.allMiniMapSprites.add(sprite.minisprite)
#            gsprite.groupsprites.remove(sprite)
        
        if groupemptied:
            self.view.allMapSprites.remove(gsprite)
            self.view.allMiniMapSprites.remove(gsprite.minisprite)
            if selectunit:
                selectedsprite = self.GetObjectSprite(clickedUnit,self.view.allMapSprites)
                self.view.selectionWindowSpritesUpper.remove(gsprite)
            #self.view.selectionWindowSpritesLower.remove(sprite)
        elif selectunit:
            selectedsprite = gsprite
            
        if selectunit:
            self.view.updateSelectionWindow()
            self.SelectUnit(selectedsprite, True)

    def umpuVisChange(self):
        if not self.view.puvis:
            self.cutSelectionToMyNationUnits()
            if self.view.selectedSprite:
                #print 'space'
                unit = self.view.selectedSprite.object
                
                self.mastercontroller.SwitchController( 'popup' )
        
                print 'puvis1', threading.currentThread()
                #wx.CallAfter(self.view.gcpan.ShowUnitModePopUp, event.uid, event.stealth)
                self.pguctrl.UpdateUMPChoices(unit)
                self.pguctrl.ShowUnitModePopUp()
                self.pguctrl.HideTopPanel()
#                    wx.CallAfter(self.view.gcpan.UpdateUMPChoices, unit)
#                    wx.CallAfter(self.view.gcpan.ShowUnitModePopUp)
#                    wx.CallAfter(self.view.gcpan.HideTopPanel)
                self.view.puvis = 1
                print 'puvis = 1'
                print 'puvis2', threading.currentThread()
                
#            else:
#                #print 'space'
##                group = self.view.selectedObj.object
#                
#                self.mastercontroller.SwitchController( 'popup' )
#        
##                    print 'puvis1', threading.currentThread()
#                #wx.CallAfter(self.view.gcpan.ShowUnitModePopUp, event.uid, event.stealth)
#                objlist = self.objectListFromSpritelist(self.view.selectedSprites)
#                settings, gensettings = self.game.unitActions.findMultiunitModeSettings(objlist)
##                settings = group.findGroupModeSettings(self.game, useproposed = True)
#                
#                self.pguctrl.UpdateGMPChoices(objlist, gensettings, self.game)
#                self.pguctrl.ShowGroupModePopUp()
#                self.pguctrl.HideTopPanel()
##                    wx.CallAfter(self.view.gcpan.UpdateGMPChoices, group, settings, self.game)
##                    wx.CallAfter(self.view.gcpan.ShowGroupModePopUp)
##                    wx.CallAfter(self.view.gcpan.HideTopPanel)
#                self.view.puvis = 1
#                print 'puvis = 1'
#                print 'puvis2', threading.currentThread()
        else:
            if self.view.selectedSprite:
                #wx.CallAfter(self.view.gcpan.HideUnitModePopUp)
#                wx.CallAfter(self.view.gcpan.setFocus)
                self.pguctrl.HideUnitModePopUp()
#                    self.view.gcpan.HideUnitModePopUp() # if use wx.CallAfter here,  mousemovement events cause errors
                self.view.puvis = 0
                self.pguctrl.ShowTopPanel()
#                    wx.CallAfter(self.view.gcpan.ShowTopPanel)
                print 'puvis = 0'
                print 'puinvis', threading.currentThread()
                self.mastercontroller.SwitchController( 'mainmap' )
                
#    def cutSelectionToMyNationUnits(self):
#        spritelist = []
#        sp = self.view.selectedSprite
#        if hasattr(sp,'object') and sp.type == 'unit':
#            obj = sp.object
#            if obj.nation == self.game.mynation:
#                spritelist.append(sp)
#        self.setSelectionToSpritelist(spritelist,False)                    

    def objectListFromSpritelist(self, spritelist):
        objlist = []
        for sp in spritelist:
            if hasattr(sp,'object'):
                if sp.object:
                    objlist.append(sp.object)
        return objlist

    def spritelistFromobjlist(self, objlist):
        spritelist = []
        for obj in objlist:
            sprite = self.GetObjectSprite(obj, self.view.allMapSprites)
            if sprite:
                spritelist.append(sprite)
        return spritelist

    def evalSpriteForMove(self,sprite, pos):
        moveable = None
        if hasattr(sprite,'object') and sprite.type == 'playerchar':
            if self.game.myprofname == self.game.charsplayer[sprite.object.name]:     # is selection my own char?
                if self.game.move_mode == 'phased':
                    if pos in sprite.object.allowed_move_tiles:
                        moveable = sprite
                else:
                    ords = sprite.object.orders
                    if not ords or ords[-1][0] == 'move':
                        allowed, cost = eval_free_move_to_tile(sprite.object, sprite.object.lastOrderedPos, pos, self.game)
                        if allowed:
                            moveable = sprite
        return moveable
    
    def add_sprites_to_lists(self):
        # add player sprites to vis list
        for pcharid in self.game.charnamesid.values():
            pchar = self.game.objectIdDict[pcharid]
            sp = self.AssembleSprite(pchar)
            self.view.allMapSprites.add(sp)
            
    def show_sprite(self, sp):
        self.view.allMapSprites.add(sp)
        
    def hide_sprite(self, sp):
        self.view.allMapSprites.remove(sp)

    def set_selection_to_object(self,event):
        spr = self.GetObjectSprite(event.obj, self.view.allMapSprites)
        self.setSelectionToSprite(spr, True)
    
    #----------------------------------------------------------------------
    def Notify(self, event):

        #if isinstance( event, CreateUnitEvent ):
        #   self.CreateUnit( event.unit )

        if isinstance( event, SpriteSelectedEvent ):
            self.setSelectionToSprite( event.sprite, event.left_click )
#            for sS in event.spritelist:
#                object = sS.object
                        
#            print am, len(am)

        elif isinstance( event, PursuedUnitSelectedEvent ):
            self.SelectPursuedUnit( event.unitSprite )

        elif isinstance( event, ClearSelectionEvent ):
            self.clearAllSelectionGraphics(event.updatemap)
#            self.ClearSelection(event.updatemap)

        elif isinstance( event, ClearPursuedSelectionEvent ):
            sprite = self.view.selectedSprite
            self.setSelectionToSprite(sprite)
#            self.ClearPursuedSelection(event.updatemap)

        elif isinstance( event, MoveOrder_View ):
            self.NewMoveOrder(event.unit, event.path)

        elif isinstance( event, ShowOrders):

            self.showOrders()
            eV = UpdateMap()
            queue.put(eV)

        elif isinstance( event, UmpuVisChange):
            
            self.umpuVisChange()
            
        elif isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance(event, RefreshAllSpritesEvent):
            self.refreshAllVisSprites()
            
            
        elif isinstance(event, AllInitUnitsCreated):

#            self.InitUV()
            self.SV = self.view.spriteVisuals

            MyNation = self.game.Nations[self.game.mynation]
            MyTeam = MyNation.team

            for n in self.game.nations:
                if self.game.Nations[n].team == MyTeam:
                    Na = self.game.Nations[n]
                    for uid in Na.units:
                        u = self.game.objectIdDict[uid]
                        self.show_sprite_of_object(u, updatemap = False)
                        #ev = UnitPlaceEvent(u)
                        #self.evManager.Post( ev )

            for c in self.game.citydict.values():
                self.show_sprite_of_object(c,False)
                #self.AssembleObjectSprite(c)
                #citySprite = self.AssembleCitySprite(c)
                #self.view.citySprites.add(citySprite)
                
            #print self.view.allMapSprites.layers(), self.view.allMapSprites.get_sprites_from_layer(70)

        #elif isinstance(event, TurnResolved):
            #self.ClearSelection()
            #eV = ToggleAllowOrders()    # turn ability to give orders back on (which is immediately impeded by showing of movie)
            #queue.put(eV)
            #eV = ShowMovie(event.mm, True, event.amhost)
            #queue.put(eV)
            ev = PassUnitViewRef(self)
            queue.put(ev)
            
            eV = UpdateMap()
            queue.put(eV)

        elif isinstance( event, MapZoomEvent ):
            self.update_all_object_sprite_images_and_positions()
            
        elif isinstance( event, HandleGroupCreationVisuals ):
            self.handleGroupCreationVisuals(event)
            
        elif isinstance( event, HandleGroupLeavingVisuals ):
            self.handleGroupLeavingVisuals(event)

        elif isinstance( event, refreshAllSprites ):
            self.refreshAllSpritesVisToTeam(event.team)

        elif isinstance( event, SelectRectEvent ):
            self.selectRectEvent(event.pos1, event.pos2)

        elif isinstance( event, DeleteLastOrderForSelectedSprite ):
            sp = self.view.selectedSprite
            if hasattr(sp,'object') and sp.type == 'playerchar':
                obj = sp.object
                if obj.can_choose_orders():
                    ev = OrderDeleteLastOrderEvent(obj)
                    queue.put(ev)
#            ev = ShowOrders()
#            queue.put(ev)
#            ev = UpdateMap()
#            queue.put(ev)

#        elif isinstance( event, GatherIntoGroup ):
#            objlist = self.objectListFromSpritelist(self.view.selectedSprites)
#            samepos = self.game.unitActions.CheckForSamePos(objlist)
#            if samepos:
#                ev = CreateMovementGroup(objlist, objlist[0].pos)
#            else:
#                ev = ChangeGatherMode()
#            queue.put(ev)
            
            
        elif isinstance( event, ShowMovementGroupWarning1 ):
            
            mgroup = event.mgroup
            objlist = event.objlist
            pos = event.pos
            
            self.mastercontroller.SwitchController( 'pguonly' )
    
            self.pguctrl.ShowGroupWarning1PopUp(mgroup, objlist, pos)

        elif isinstance( event, HideMovementGroupWarning1 ):
            
            self.mastercontroller.SwitchController( 'mainmap' )
    
            self.pguctrl.HideGroupWarning1PopUp()

  
        elif isinstance( event, setSelectionToGroupEvent ):
            self.setSelectionToGroup(event.mgroup)        

        elif isinstance( event, SetSelectionToObject ):
            self.set_selection_to_object(event)

'''     elif isinstance(event, UnitModePopupEvent):
            if not self.view.puvis:
                self.umpu = UnitModePopUp(event.unit, background = (200,200,200))
                self.umpu.open()
                self.view.puvis = 1
                self.view.view_refresh_needed = 1
            else:
                event.unit.stealth = self.umpu.g.value
                self.umpu.close()
                self.view.puvis = 0
                self.view.view_refresh_needed = 1'''


