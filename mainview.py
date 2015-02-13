import Queue

import os

import pygame
from pygame.locals import *

from math import *
import random
from copy import deepcopy

import yaml
from pgu import gui

from events import *
from evmanager import *
from game import *
from movie import *
#from controllers import *
#from unitview import *
#from numpy import *
from internalconstants import *
from userconstants import *
from soundview import *
import spritevisuals
from fontdefs import *
import view_utils
import toppanel
import info_popup
import mobile_object
import info_dialog_utils


'''class ViewCircleSprite(pygame.sprite.Sprite):
    def __init__( self ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (64,64) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        self.rect  = unitSurf0.get_rect()
        pygame.draw.rect( unitSurf0, (255,255,255), self.rect, 4)   # the selected sprite

        self.image = unitSurf0'''

#------------------------------------------------------------------------------
class MainView:
    """..."""
    def __init__(self, evManager, windw, pguapp, pguctrl):
        self.evManager = evManager
        listencats = ["updateview"]
        self.evManager.RegisterListener( self, listencats )

        self.window = windw
        self.pguapp = pguapp
        self.pguctrl = pguctrl
        
        self.mainscrsize = self.window.get_size()

#        pygame.init()

        self.mapViewPortDim = (self.mainscrsize[0],self.mainscrsize[1]-bottom_window_heights - toppanel_height)
        self.toppanelDim = (self.mainscrsize[0], toppanel_height)
        self.minimapViewPortDim = (200,bottom_window_heights)
        self.infowindowdim = (150,bottom_window_heights)
        self.selectionwindim = (self.mainscrsize[0]-350,bottom_window_heights)


        #self.window = pygame.display.set_mode( self.screendim, screenflag )
        self.window.fill( splashscreencolor )
        pygame.display.update()

        self.innerrect = pygame.Rect(scroll_width,scroll_width,self.mainscrsize[0]-2*scroll_width,self.mainscrsize[1]-2*scroll_width)
        self.mapViewPortRect = pygame.Rect(0,toppanel_height,self.mapViewPortDim[0],self.mapViewPortDim[1])
        self.toppanelrect = pygame.Rect(0,0,self.mainscrsize[0],toppanel_height)
        self.minimaprect = pygame.Rect(0,self.mainscrsize[1]-200,self.minimapViewPortDim[0],self.minimapViewPortDim[1])
        self.infowindowrect = pygame.Rect(self.mainscrsize[0]-150,self.mainscrsize[1]-200,self.infowindowdim[0],self.infowindowdim[1])
        self.selectionwinrect = pygame.Rect(200,self.mainscrsize[1]-200,self.selectionwindim[0],self.selectionwindim[1])

        #self.dimminiMapTerrain = pygame.Surface(self.minimapViewPortDim).convert()
        self.toppanelBackground = pygame.Surface(self.toppanelDim).convert()
        self.toppanelBackground.fill((100,100,150))
        self.infoWindowBackground = pygame.Surface(self.infowindowdim).convert()
        self.infoWindowBackground.fill(infowindowbackgroundcolor)
        self.selectionwinBackground = pygame.Surface(self.selectionwindim).convert()
        self.selectionwinBackground.fill((150,50,100))

        self.allMapSprites = pygame.sprite.LayeredUpdates()
        self.allMiniMapSprites = pygame.sprite.LayeredUpdates()
        self.selectionWindowSpritesUpper = pygame.sprite.LayeredUpdates()
        self.selectionWindowSpritesLower = pygame.sprite.LayeredUpdates()
        self.targetting_mode_sprites_under_click = pygame.sprite.LayeredUpdates()
        #self.myUnitSprites = pygame.sprite.OrderedUpdates()   # my unit sprites, for whole map
        #self.viewCircleSprites = pygame.sprite.Group()
        #self.miniviewCircleSprites = pygame.sprite.Group()
        #self.teamUnitSprites = pygame.sprite.OrderedUpdates()

        #self.otherteamVisUnitSprites = pygame.sprite.OrderedUpdates()
        self.otherteamUnitSprites = pygame.sprite.Group()   # don't think this is used any more
        
        #self.viewedTileSprites = pygame.sprite.Group()

        #self.visOrderSprites = pygame.sprite.OrderedUpdates()
#        self.order_lines = []
#        self.order_sprites = []
        self.party_sprites = []
        self.monster_sprites = []
        self.object_sprites = []
        #self.OrderLines = []

        #self.citySprites = pygame.sprite.Group()

        self.selectedObj = None     # not used atm
        self.SWselectedObj = None   # not used atm
        #self.subselectedObj = None
        self.subselectedLoc = None
        self.pursuedObj = None
        self.SWpursuedObj = None
        #self.selectionSprites = pygame.sprite.OrderedUpdates()  # only one for now, but may implement multiple selection later
        self.selectedSprite = None
        self.selectedSpriteBackup = None
        self.left_click_sprite_list = []
        self.right_click_sprite_list = []
        self.selectionContains = {}
        self.selectionContains['mynationunits'] = False
        self.selectionContains['myteamunits'] = False
        self.selectionContains['mycities'] = False
        self.pursuedSprites = []

        #self.teamColors = [[255,0,0], [0,128,128]]

        self.mapRect = pygame.Rect(0,0,self.mapViewPortDim[0], self.mapViewPortDim[1])
                # rect describing map coords of viewed window
        self.maxtopleft = (0,0) # will be maximum map topleft after we know gameMap size

        self.view_refresh_needed = 1

#        self.medfont = pygame.font.Font(None,14)
        self.medfont_linesize = fontdefault14.get_linesize()
        self.font20_linesize = fontdefault20.get_linesize()
        self.font22_linesize = fontdefault22.get_linesize()
        
        self.infowindowborder = 5
        self.iwfieldbgsurf = pygame.Surface( (self.infowindowdim[0] - self.infowindowborder, self.medfont_linesize)).convert()
        self.iwfieldbgsurf.fill(infowindowbackgroundcolor)
        self.iwfield = []
        self.oldiwfield = []
        self.iwfieldrect = []
        self.num_iw_fields = 5
        self.refreshiw = False
        for iiw in range(self.num_iw_fields):
            self.iwfield.append('')
            self.iwfieldrect.append(pygame.Rect(self.infowindowrect.left+self.infowindowborder, self.infowindowrect.top+self.infowindowborder + iiw*self.medfont_linesize ,self.infowindowrect.width - self.infowindowborder, self.medfont_linesize))
            self.oldiwfield.append('')

#       self.ctainer = gui.Container(align=-1,valign=-1)
#       self.app.init(self.ctainer)

        self.puvis = 0
        self.showallunitorders = True

        
#        self.zoomidx = 2
        
        self.mouseOverEventLocked = False
        self.mapscrollLocked = False
        
        #self.currentMapPosForSelectedSprite = None
        self.oldmapposlist = []
        #self.spritecyclelist = []
        
        self.viewcirclelayer = 10
        self.fixed_item_layer = 20
        self.carried_item_layer = 25
        self.otherteamvislayer = 30
        self.myteamlayer = 40
        self.orderlineslayer = 50
        self.orderspriteslayer = 60
        self.myspriteslayer = 70
        self.selectedlayer = 80
        self.allowed_move_layer = 85
        self.selectrectlayer = 90
        
        self.selectRectSprite = None
        
        self.soundView = SoundView(evManager, self)
        
        self.movie = Movie(self.evManager, self, self.soundView)
        self.atmovieend = True
        self.movierunning = False
        
        self.importMapTiles()
        self.numzooms = len(zoomfactors)
        
        self.createTileViewMasks()
        self.create_allowed_tile_mask()
        self.create_effect_area_mask()
#        self.use_effect_area_mask = False
#        self.cleanup_count = 0      # for clearing out game.tilesWithinView
        
        self.active_char = None
        self.viewing_map_section = None
        self.target_mode = False
        self.old_target_mode = False
        
        self.allowed_moves = set()
        self.tiles_now_not_allowed = set()
        self.allowed_tiles_overlay = set()
#        self.allowed_target_sprites = set()
        self.effect_area_overlay = set()
        self.effect_area_func = None
        self.set_effect_area_func(None)
        self.use_effect_area_func = False

        
        self.old_map_pos_hover = None
        self.hover_sprite_dict = {}
        self.hover_sprite_dict['playerchar'] = None
        self.hover_sprite_dict['monster'] = None
        self.hover_sprite_dict['carried_item'] = []
        self.hover_sprite_dict['fixed_item'] = []
        self.hover_sprite_dict['trap'] = None
        self.hover_sprite_dict['other_mobj'] = None
        self.hover_sprite_list = []
        self.num_sprites_under_mouse = 0
        

        self.primary_floating_menu_rect = None
        self.secondary_floating_menu_rect = None
        self.modal_window_rect = None
        self.nonmodal_popup_rect = None
        
        self.popup_floating_rect = None
        self.default_hover_popup_data = {}
        self.default_hover_popup_data['default'] = {}
        self.default_hover_popup_data['default']['style'] = {  'padding_left':1, \
                                'padding_right':1, \
                                'padding_top':1, \
                                'padding_bottom':1, \
                                'border_left':0, \
                                'border_right':0, \
                                'border_top':0, \
                                'border_bottom':0, \
                                'border_color':(255,255,255,255), \
                                'background':(0,0,0,0)} 
#                                ('background','hover'):(255,255,255,50), \
#                                ('background','down'):(255,255,255,100), \
#                                ('border_color','hover'):(0,0,0,0), \
#                                ('border_color','down'):(0,0,0,0) \
#                              }
        
        self.default_hover_popup_data['section'] = {}
        self.default_hover_popup_data['section'][1] = {}
        self.def_hover_popup_font = fontdefault16
        
#        self.fontFreebooter26 = pygame.font.Font(resourcepath + 'freebooter.ttf',26)
#        self.fontFreebooter36 = pygame.font.Font(resourcepath + 'freebooter.ttf',36)

        self.client_msg_list = []
        self.max_num_client_msgs = 200
        
    def transferUVref(self,uvref):
        self.uv = uvref        
        
    def transferCVref(self,cvref):
        self.cv = cvref        
        
    def sendControllerRefToView(self,controllerref):
        self.mastercontroller = controllerref
        self.uv.sendControllerRefToUv(controllerref)
#        self.cv.sendControllerRefToCv(controllerref)

    #----------------------------------------------------------------------
    
    def add_client_msg(self,msg):
        # msg is a pygame surface containing text rendered onto the surface
        
        if len(self.client_msg_list) >= self.max_num_client_msgs:
            self.client_msg_list.pop()
        self.client_msg_list.insert(0,msg)

    def show_timed_msg(self,msg, add_to_list = True):
        # msg is either a string or a dictionary with text and some formatting info
        surf = info_dialog_utils.return_msg_on_surface(msg, 800, 600)
        self.pguctrl.add_timed_message(surf,50,50)
        if add_to_list:
            self.add_client_msg(surf)
        
    def UpdateMiniMap(self):
        
        #self.miniMapAll.blit(self.dimminiMapTerrain,(0,0))
        self.miniMapAll.blit(self.viewedminiMapTerrain,(0,0))
        
        self.allMiniMapSprites.draw(self.miniMapAll)

        '''self.miniviewCircleSprites.draw(self.miniMapAll)

        trec = pygame.Rect(0,0,4,4)
        # put pixels (or small squares) for units on minimap
            
        for s in self.myUnitSprites:
            trec.center = s.minimap_pos
            pygame.draw.rect(self.miniMapAll,s.color, trec)

        for s in self.otherteamVisUnitSprites:
            trec.center = s.minimap_pos
            pygame.draw.rect(self.miniMapAll,s.color, trec)'''

        self.ShowMiniMapViewBox()
        #todo:  make a minimap surface that holds current data (including unit pixels)
        # but not viewbox rect -- to remove need to recalculate unit pixels during scrolling

    def ShowMiniMapViewBox(self):
        (mbleft,mbtop) = self.convertVSPixToMiniMapVSPix( (self.mapRect.left, self.mapRect.top) )
        #self.minibox.left = int(round(self.mapRect.left*self.MMConvFactor))
        #self.minibox.top = int(round(self.mapRect.top*self.MMConvFactor))
        self.minibox[self.zoomlevel].left = mbleft
        self.minibox[self.zoomlevel].top = mbtop

        # would it be faster to blit an image with this rect, or draw a rect?
        pygame.draw.rect( self.miniMapAll, (255,255,255), self.minibox[self.zoomlevel], 1)


    def show_default_info_popup(self, msg):

        raw_data = {}
        raw_data['text'] = {}
        raw_data['text'][0] = {}
        raw_data['text'][0]['string'] = msg 
        raw_data['text'][0]['color'] = (200,200,200,255)
        raw_data['text'][0]['font'] = fontdefault20
        raw_data['text_panel_format'] = {'background': (0,0,250,255)}
        
        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
        raw_data['buttons'] = {}
        raw_data['buttons'][0] = {}
        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
        raw_data['buttons'][0]['function'] = 'close'
    #    raw_data['buttons'][0]['format'] = {'background':(250,0,0,150)}
        
        infpw = info_popup.PopupWithOneColumnTextAndButtonsBelow(raw_data, (0.5,0.75,0.5,0.75,True), self.mapViewPortRect, toppanel_height, background = (0,0,0,0))
        self.modal_window_rect = infpw.rect
        self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
        ev = SwitchToModalControllerEvent(infpw)
        queue.put(ev)

    def show_default_choice_popup(self, data, choice_func):
        infpw = info_popup.ChoicePopup(data, choice_func, (0.5,0.75,0.5,0.75,True), self.mapViewPortRect, toppanel_height, ctrl = self.mastercontroller ,background = (222,222,222,255))
        self.modal_window_rect = infpw.rect
        self.pguctrl.show_modal_window(infpw, infpw.rect.topleft)
        ev = SwitchToModalControllerEvent(infpw)
        queue.put(ev)

    def PositionMainScreen(self,newtopleft,dorefresh = True):
            self.mapRect.left = newtopleft[0]
            self.mapRect.top = newtopleft[1]
#            pzrl = newtopleft[0] + self.MapTL[self.zoomlevel][0]
#            pzrt = newtopleft[1] + self.MapTL[self.zoomlevel][1]
#            self.preZoomedRect[self.zoomlevel].left = int(round(newtopleft[0]/zoomfactors[self.zoomlevel]))
#            self.preZoomedRect[self.zoomlevel].top = int(round(newtopleft[1]/zoomfactors[self.zoomlevel]))
            self.UpdateMiniMap()
            if dorefresh:
                self.view_refresh_needed = 1
                print 'mainview, vrn1'
            

    def RequestMapMove(self, topleftreq, dorefresh= True):
        xreq = topleftreq[0]
        yreq = topleftreq[1]
        moveit = 0
        if xreq < 0:
            newx = 0
        elif xreq > self.maxtopleft[self.zoomlevel][0]:
            newx = self.maxtopleft[self.zoomlevel][0]
        else:
            newx = xreq
#        if newx != self.mapRect.left:
#            moveit = 1

        if yreq < 0:
            newy = 0
        elif yreq > self.maxtopleft[self.zoomlevel][1]:
            newy = self.maxtopleft[self.zoomlevel][1]
        else:
            newy = yreq
#        if newy != self.mapRect.top:
#            moveit = 1

        self.preZoomedRect[self.zoomlevel].left = int(round(newx/zoomfactors[self.zoomlevel]))
        self.preZoomedRect[self.zoomlevel].top = int(round(newy/zoomfactors[self.zoomlevel]))
        
#        if moveit:
#            self.PositionMainScreen((newx,newy), dorefresh)
        self.PositionMainScreen((newx,newy), dorefresh)
            
            
    def changeZoomReq(self, event):
        
        zoomchanged = 0
        
        if event.zoom == 0:
            if self.zoomlevel < self.numzooms-1:
                self.oldzoomlevel = self.zoomlevel
                self.mouseOverEventLocked = True
                self.mapscrollLocked = True
                self.zoomlevel += 1
                zoomchanged = 1
        else:
            if self.zoomlevel > 0:
                self.oldzoomlevel = self.zoomlevel
                self.mouseOverEventLocked = True
                self.mapscrollLocked = True
                self.zoomlevel -= 1
                zoomchanged = 1
                
        if zoomchanged:
            eV = MapZoomEvent(event.pos)
            queue.put(eV)
            
    def changeZoom(self, posreq):
            ozl = self.oldzoomlevel
            zl = self.zoomlevel
            oldwidth = self.viewableSurfDim[ozl][0]
            oldheight = self.viewableSurfDim[ozl][1]
            
            vspix = self.convertWholeViewPortPixToVSPix(posreq)

            if self.MapTL[zl] == (0,0) and self.MapTL[ozl] == (0,0):
                # neither old nor new viewable surface has non-map areas
                # so can preserve both mouse position on map and mouse position on screen

                widthfrac =  float(vspix[0])/oldwidth
                heightfrac = float(vspix[1])/oldheight
                
                mapVPPix = self.convertWholeViewPortPixToMapViewPortPix(posreq)
                scrwidfrac = float(mapVPPix[0])/self.mapViewPortDim[0]
                scrheifrac = float(mapVPPix[1])/self.mapViewPortDim[1]
            
                leftreq = int(round(widthfrac*self.viewableSurfDim[zl][0] - self.mapViewPortDim[0]*scrwidfrac))  
                topreq = int(round(heightfrac*self.viewableSurfDim[zl][1] - self.mapViewPortDim[1]*scrheifrac))
                
                self.RequestMapMove( (leftreq, topreq), False )
                
            else:  
                # zooming in or out from a viewable surface that has non-map areas
                # so preserve mouse position on map but force mouse to move on screen
                
                oldmapxfrac = (vspix[0] - self.MapTL[ozl][0]) / float(self.mapPixDim[ozl][0])
                if oldmapxfrac < 0:
                    oldmapxfrac = 0.
                elif oldmapxfrac > 1:
                    oldmapxfrac = 1.
                oldmapyfrac = (vspix[1] - self.MapTL[ozl][1]) / float(self.mapPixDim[ozl][1])
                if oldmapyfrac < 0:
                    oldmapyfrac = 0.
                elif oldmapyfrac > 1:
                    oldmapyfrac = 1.
                
                newmapxpix = int(round( oldmapxfrac * (self.mapPixDim[zl][0]-1) ))
                newmapypix = int(round( oldmapyfrac * (self.mapPixDim[zl][1]-1) ))
                
                newmapVSxpix = newmapxpix + self.MapTL[zl][0]
                newmapVSypix = newmapypix + self.MapTL[zl][1]
                
                # request that same map position be in center
                newleftreq = int(round(newmapVSxpix - self.mapViewPortDim[0]/2.))
                newtopreq = int(round(newmapVSypix - self.mapViewPortDim[1]/2.))
                
                self.RequestMapMove( (newleftreq, newtopreq), False )
                
                newmousex = newmapVSxpix - self.mapRect.left
                newmousey = newmapVSypix - self.mapRect.top + toppanel_height
                pygame.mouse.set_pos( (newmousex, newmousey) )
                     
            self.mouseOverEventLocked = False
            self.mapscrollLocked = False
            
            eV = UpdateMap()
            queue.put(eV)
            
                
    def changeZoom_old(self, posreq):
            ozl = self.oldzoom
            zl = self.zoomlevel
            oldwidth = self.viewableSurfDim[ozl][0]
            oldheight = self.viewableSurfDim[ozl][1]
            '''if self.zoomlevel == 1:
                self.gameTerrain = self.gameTerrain1
                self.dimTerrain = self.dimTerrain1
                self.viewableMap = self.viewableMap1
                self.viewableSurfWidth = self.viewableSurfWidth1
                self.viewableSurfHeight = self.viewableSurfHeight1
                self.mapInViewPortRect = self.mapInViewPortRect1 
                self.MapTL = self.MapTL1
                #self.hor_conv = self.hor_conv1
                #self.ver_conv = self.ver_conv1
                self.MMConvFactor = self.MMConvFactor1
                self.minibox = self.minibox1
                #print 'dimzoom', self.gameTerrain.get_at( (300,300) )
          
            elif self.zoomlevel == 2:
                self.gameTerrain = self.gameTerrain2
                self.dimTerrain = self.dimTerrain2
                self.viewableMap = self.viewableMap2
                self.viewableSurfWidth = self.viewableSurfWidth2
                self.viewableSurfHeight = self.viewableSurfHeight2
                self.mapInViewPortRect = self.mapInViewPortRect2 
                self.MapTL = self.MapTL2
                #self.hor_conv = self.hor_conv2
                #self.ver_conv = self.ver_conv2
                self.MMConvFactor = self.MMConvFactor2
                self.minibox = self.minibox2
          
            elif self.zoomlevel == 3:
                self.gameTerrain = self.gameTerrain3
                self.dimTerrain = self.dimTerrain3
                self.viewableMap = self.viewableMap3
                self.viewableSurfWidth = self.viewableSurfWidth3
                self.viewableSurfHeight = self.viewableSurfHeight3
                self.mapInViewPortRect = self.mapInViewPortRect3 
                self.MapTL = self.MapTL3
                #self.hor_conv = self.hor_conv3
                #self.ver_conv = self.ver_conv3
                self.MMConvFactor = self.MMConvFactor3
                self.minibox = self.minibox3
                
            elif self.zoomlevel == 4:
                self.gameTerrain = self.gameTerrain4
                self.dimTerrain = self.dimTerrain4
                self.viewableMap = self.viewableMap4
                self.viewableSurfWidth = self.viewableSurfWidth4
                self.viewableSurfHeight = self.viewableSurfHeight4
                self.mapInViewPortRect = self.mapInViewPortRect4
                self.MapTL = self.MapTL4
                #self.hor_conv = self.hor_conv4
                #self.ver_conv = self.ver_conv4
                self.MMConvFactor = self.MMConvFactor4
                self.minibox = self.minibox4
                
            self.maxtopleft = (self.viewableSurfWidth-self.mainViewPortDim[0], self.viewableSurfHeight-self.mainViewPortDim[1])'''
            
            vspix = self.convertWholeViewPortPixToVSPix(posreq)
            
            #widthfrac =  float(self.mapRect.left + posreq[0])/float(oldwidth)
            #heightfrac = float(self.mapRect.top + posreq[1])/float(oldheight)
            

            if self.MapTL[zl] == (0,0) and self.MapTL[ozl] == (0,0):
                # neither old nor new viewable surface has non-map areas
                # so can preserve both mouse position on map and mouse position on screen

                widthfrac =  float(vspix[0])/oldwidth
                heightfrac = float(vspix[1])/oldheight
                
                mapVPPix = self.convertWholeViewPortPixToMapViewPortPix(posreq)
                scrwidfrac = float(mapVPPix[0])/self.mapViewPortDim[0]
                scrheifrac = float(mapVPPix[1])/self.mapViewPortDim[1]
            
                leftreq = int(round(widthfrac*self.viewableSurfDim[zl][0] - self.mapViewPortDim[0]*scrwidfrac))  
                topreq = int(round(heightfrac*self.viewableSurfDim[zl][1] - self.mapViewPortDim[1]*scrheifrac))
                
                #newrectreq = self.mapRect.move(0,0)
                #leftreq = int(round(widthfrac*self.viewableSurfWidth - self.mainViewPortDim[0]/2))  
                #topreq = int(round(heightfrac*self.viewableSurfHeight - self.mainViewPortDim[1]/2))
                
                self.RequestMapMove( (leftreq, topreq), False )
                
            else:  
                # zooming in or out from a viewable surface that has non-map areas
                # so preserve mouse position on map but force mouse to move on screen
                
                oldmapxfrac = (vspix[0] - self.MapTL[ozl][0]) / float(self.mapPixDim[ozl][0])
                if oldmapxfrac < 0:
                    oldmapxfrac = 0.
                elif oldmapxfrac > 1:
                    oldmapxfrac = 1.
                oldmapyfrac = (vspix[1] - self.MapTL[ozl][1]) / float(self.mapPixDim[ozl][1])
                if oldmapyfrac < 0:
                    oldmapyfrac = 0.
                elif oldmapyfrac > 1:
                    oldmapyfrac = 1.
                
                newmapxpix = int(round( oldmapxfrac * (self.mapPixDim[zl][0]-1) ))
                newmapypix = int(round( oldmapyfrac * (self.mapPixDim[zl][1]-1) ))
                
                newmapVSxpix = newmapxpix + self.MapTL[zl][0]
                newmapVSypix = newmapypix + self.MapTL[zl][1]
                
                # request that same map position be in center
                newleftreq = int(round(newmapVSxpix - self.mapViewPortDim[0]/2.))
                newtopreq = int(round(newmapVSypix - self.mapViewPortDim[1]/2.))
                
                self.RequestMapMove( (newleftreq, newtopreq), False )
                
                newmousex = newmapVSxpix - self.mapRect.left
                newmousey = newmapVSypix - self.mapRect.top + toppanel_height
                pygame.mouse.set_pos( (newmousex, newmousey) )
                     
                
            
            #print self.mapRect, posreq, (leftreq, topreq)
            
            #print 'cz'
            
            #self.RequestMapMove( (leftreq, topreq), False )
            
            #if self.mapRect.left != leftreq:
                #newmousex = 
                
            self.mouseOverEventLocked = False
            self.mapscrollLocked = False
            
            #newmousex = round(widthfrac*self.viewableSurfWidth - self.mapRect.left)
            #newmousey = round(heightfrac*self.viewableSurfHeight - self.mapRect.top)
            #pygame.mouse.set_pos( (newmousex, newmousey) )
            
            eV = UpdateMap()
            queue.put(eV)
            
    '''def blitInPieces(self,gt,md,mm):
        
        chunksize = 1000
        
        numwide = int(ceil(float(md[0])/float(chunksize)))
        numtall = int(ceil(float(md[1])/float(chunksize)))
        
        llist = []
        wlist = []
        tlist = []
        hlist = []
        
        for i in range(numwide):
            llist.append(i*chunksize)
            if i+1 == numwide:
                wlist.append(md[0]-i*chunksize)
            else:
                wlist.append(chunksize)
                
        for i in range(numtall):
            tlist.append(i*chunksize)
            if i+1 == numtall:
                hlist.append(md[1]-i*chunksize)
            else:
                hlist.append(chunksize)
                
        for i in range(numwide):
            for j in range(numtall):
                temp = pygame.Surface((wlist[i],hlist[j])).convert()
                pygame.surfarray.blit_array(temp,mm[llist[i]:llist[i]+wlist[i],tlist[j]:tlist[j]+hlist[j]])
                #print 'bip', temp.get_at( (12,300) )
                gt.blit(temp,(llist[i],tlist[j]))
                #print 'bip2', gt.get_at( (512,300) )'''
                
    def calcMapEdgeEffects(self, PixDim, MapScrDim):
        '''
        viewableSurfWidth is either the total pixel width of the map, or the pixel width of the mapViewPort,
        whichever is greater.  So it's at least the mapViewPort size (if zoomed way out), and usually larger.
        
        mapOnScreenWidth is either the total pixel width of the map, or the pixel width of the mapViewPort,
        whichever is smaller.  So it's at most the mapViewPort size, and occasionally smaller (if zoomed way out).
        
        '''
        
        
        if PixDim[0] < MapScrDim[0]:
            viewableSurfWidth = MapScrDim[0]
            mapLeftpoint = int((viewableSurfWidth - PixDim[0])/2)
            mapOnScreenWidth = PixDim[0]
        else:
            viewableSurfWidth = PixDim[0]
            mapLeftpoint = 0
            mapOnScreenWidth = MapScrDim[0]
            
        if PixDim[1] < MapScrDim[1]:
            viewableSurfHeight = MapScrDim[1]
            mapToppoint = int((viewableSurfHeight - PixDim[1])/2)
            mapOnScreenHeight = PixDim[1]
        else:
            viewableSurfHeight = PixDim[1]
            mapToppoint = 0
            mapOnScreenHeight = MapScrDim[1]
            
        return (viewableSurfWidth,viewableSurfHeight), (mapLeftpoint,mapToppoint), (mapOnScreenWidth,mapOnScreenHeight)
    
    def convertMapPosToViewSurfPos(self, pos, usedefaultzoom = False):
        
        # This gives the center pixel for a map position
        if usedefaultzoom:
            zl = self.defaultzoomlevel
        else:
            zl = self.zoomlevel
        tps = self.tps[zl]
        
        xpos = int(round( tps*(pos[0] + 0.5) ))
        ypos = int(round( tps*(pos[1] + 0.5) ))
        
        '''if self.zoomlevel == 1:
            zoomfactor = 0.5
        elif self.zoomlevel == 2:
            zoomfactor = 1.0                        
        elif self.zoomlevel == 3:
            zoomfactor = 2.0                        
        elif self.zoomlevel == 4:
            zoomfactor = 4.0
            
        xpos = int(round(pos[0]*zoomfactor))                            
        ypos = int(round(pos[1]*zoomfactor))'''
        
        xVSpos = xpos + self.MapTL[zl][0]
        yVSpos = ypos + self.MapTL[zl][1]
        
        return ( (xVSpos,yVSpos) )  
    
    def convertMapPosToTLViewSurfPos(self, pos, usedefaultzoom = False):
        
        # This gives the top left pixel for a map position
        if usedefaultzoom:
            zl = self.defaultzoomlevel
        else:
            zl = self.zoomlevel
        tps = self.tps[zl]
        
        xpos = int(round( tps*pos[0] ))
        ypos = int(round( tps*pos[1] ))
        
        xVSpos = xpos + self.MapTL[zl][0]
        yVSpos = ypos + self.MapTL[zl][1]
        
        return ( (xVSpos,yVSpos) )  
    
    def convertMapPosToViewedTerrainPos(self, pos, usedefaultzoom = False):
        
        # This gives the top left pixel for a map position, but for viewed terrain
        # (no black borders, only the map)
        if usedefaultzoom:
            zl = self.defaultzoomlevel
        else:
            zl = self.zoomlevel
        tps = self.tps[zl]
        
        xpos = int(round( tps*(pos[0] + 0.5) ))
        ypos = int(round( tps*(pos[1] + 0.5) ))
        
        xVTpos = xpos
        yVTpos = ypos
        
        return ( (xVTpos,yVTpos) )  
    
    def convertMapPosToTLViewedTerrainPos(self, pos, usedefaultzoom = False):
        
        # This gives the top left pixel for a map position, but for viewed terrain
        # (no black borders, only the map)
        if usedefaultzoom:
            zl = self.defaultzoomlevel
        else:
            zl = self.zoomlevel
        tps = self.tps[zl]
        
        xpos = int(round( tps*pos[0] ))
        ypos = int(round( tps*pos[1] ))
        
        xVTpos = xpos
        yVTpos = ypos
        
        return ( (xVTpos,yVTpos) )  
    
    def convertVSPixToMapPos(self, pos, usedefaultzoom = False):
        
        if usedefaultzoom:
            zl = self.defaultzoomlevel
        else:
            zl = self.zoomlevel
        tps = self.tps[zl]
        
        # convert from pixel on visual surface to pixel on map
        xmappixpos = pos[0] - self.MapTL[zl][0]
        ymappixpos = pos[1] - self.MapTL[zl][1]
        
        xmappos = int(floor(xmappixpos/tps))
        ymappos = int(floor(ymappixpos/tps))
        
        return ( (xmappos,ymappos) )
    
    def convertWholeViewPortPixToMapPos(self,pos, usedefaultzoom = False):
    
        VSPixpos = self.convertWholeViewPortPixToVSPix(pos)
        return( self.convertVSPixToMapPos(VSPixpos, usedefaultzoom) )
      
    def convertWholeViewPortPixToVSPix(self,pos):
        
        mapVPPix = self.convertWholeViewPortPixToMapViewPortPix(pos)
        return(self.convertMapViewPortPixToVSPix(mapVPPix))
    
    def convertWholeViewPortPixToMapViewPortPix(self,pos):
    
        return(pos[0], pos[1] - toppanel_height)
    
    def convertWholeViewPortPixToSelectionWindowPix(self,pos):
    
        return(pos[0]-self.selectionwinrect.left, pos[1] - self.selectionwinrect.top)
    
    def convertMapViewPortPixToVSPix(self,pos):
    
        return(pos[0] + self.mapRect.left, pos[1] + self.mapRect.top)
    
    def convertMapPosToMiniMapPos(self,pos):
        # todo: following 2 lines will be changed when true unit position is measured in terms
        # of map coords instead of zoom 2 coords
        #xfrac = pos[0]/ (self.viewableSurfWidth2 - 2.0*self.MapTL2[0])
        #yfrac = pos[1]/ (self.viewableSurfHeight2 - 2.0*self.MapTL2[1])
        
#        xfrac = float(pos[0])/self.MapDim[0]
#        yfrac = float(pos[1])/self.MapDim[1]
        
#        xMMMappos = int(round(xfrac * self.minimapDim[0]))
#        yMMMappos = int(round(yfrac * self.minimapDim[1]))
        
        xMMMappos = int(round(pos[0] * self.MMMapConvFactor))
        yMMMappos = int(round(pos[1] * self.MMMapConvFactor))

        xMMVSpos = self.minimapTL[0] + xMMMappos
        yMMVSpos = self.minimapTL[1] + yMMMappos
        
        return ( (xMMVSpos, yMMVSpos) )
    
    def convertVSPixToMiniMapVSPix(self,pos):
        deltaxMapTLVSP = pos[0] - self.MapTL[self.zoomlevel][0]
        deltayMapTLVSP = pos[1] - self.MapTL[self.zoomlevel][1]
        
        deltaxMMTL = int(round(self.MMPixConvFactor[self.zoomlevel] * deltaxMapTLVSP))
        deltayMMTL = int(round(self.MMPixConvFactor[self.zoomlevel] * deltayMapTLVSP))
        
        xMMVSpos = self.minimapTL[0] + deltaxMMTL 
        yMMVSpos = self.minimapTL[1] + deltayMMTL
        
        if xMMVSpos < 0:
            xMMVSpos = 0
        elif xMMVSpos >= self.minimapViewPortDim[0]:
            xMMVSpos = self.minimapViewPortDim[0]-1
            
        if yMMVSpos < 0:
            yMMVSpos = 0
        elif yMMVSpos >= self.minimapViewPortDim[1]:
            yMMVSpos = self.minimapViewPortDim[1]-1
        
        return ( (xMMVSpos, yMMVSpos) )
                                  
    def convertMiniMapVSPixToVSPix(self,pos):
        deltaxMMTL = pos[0] - self.minimapTL[0]
        deltayMMTL = pos[1] - self.minimapTL[1]
        
        deltaxMapTLVSP = int(round(deltaxMMTL/self.MMPixConvFactor[self.zoomlevel]))
        deltayMapTLVSP = int(round(deltayMMTL/self.MMPixConvFactor[self.zoomlevel]))
        
        xVSpos = self.MapTL[self.zoomlevel][0] + deltaxMapTLVSP 
        yVSpos = self.MapTL[self.zoomlevel][1] + deltayMapTLVSP
        
        if xVSpos < 0:
            xVSpos = 0
        elif xVSpos >= self.viewableSurfDim[self.zoomlevel][0]:
            xVSpos = self.viewableSurfDim[self.zoomlevel][0]-1
            
        if yVSpos < 0:
            yVSpos = 0
        elif yVSpos >= self.viewableSurfDim[self.zoomlevel][1]:
            yVSpos = self.viewableSurfDim[self.zoomlevel][1]-1
        
        return ( (xVSpos, yVSpos) )
    
    def convertMiniMapVSPixToMapPos(self,pos):
        vspix = self.convertMiniMapVSPixToVSPix(pos)
        return(self.convertVSPixToMapPos(vspix))

    def importMapTiles(self):
        
        self.maptile_surfdict = {}
        thispath = os.path.join(resourcepath,'terrain.gfx')
        f = open(thispath, 'r')
        tgfx_prefs = yaml.load(f)
        f.close()
        
        
#        self.maptile_surfdict[pixsize] = {}
        for ttype,stypedict in tgfx_prefs.iteritems():
            for stype,varianttilelist in stypedict.iteritems():
                tsurf2 = []
                for varianttile in varianttilelist:
                    pathtilefn = os.path.join(terraintilespath,varianttile)
                    tsurf = pygame.image.load(pathtilefn)
                    tsurf2.append(tsurf.convert())
                self.maptile_surfdict[(ttype,stype)] = tsurf2
            
            
    def setup_map(self, map):      
        
        self.map = map
        
        self.tps = []
        self.spritesize = []
        for i, zf in enumerate(zoomfactors):
            tps = tilepixsize * zf
            self.tps.append(tps)
            sprsize = int(round(tilepixsize * spritezoomfactors[i]))
            self.spritesize.append( (sprsize,sprsize) )
            
        self.backSurf = pygame.Surface(self.mapViewPortDim).convert()
        self.defaultzoomlevel = zoomfactors.index(1.0)

#        sname = map['possiblestartpos'][0]
        first_char_name = self.game.playerschars[self.game.myprofname][0]
        first_char = self.game.objectIdDict[self.game.charnamesid[first_char_name]]
        self.viewing_map_section = first_char.map_section
        self.setMapToMapsection(self.viewing_map_section)
            
        self.toppanelWindow = pygame.Surface(self.toppanelDim).convert()
        self.toppanelWindow.blit(self.toppanelBackground,(0,0))

        self.infoWindow = pygame.Surface(self.infowindowdim).convert()
        self.infoWindow.blit(self.infoWindowBackground,(0,0))
        self.window.blit(self.infoWindow, self.infowindowrect.topleft)

        self.selectionWindow = pygame.Surface(self.selectionwindim).convert()
        self.selectionWindow.blit(self.selectionwinBackground,(0,0))

#        viewed_tiles = view_utils.find_all_tiles_viewed_by_party(self.game)
#        view_utils.adjust_view(self.game, viewed_tiles, self.viewing_map_section)
        self.tiles_with_view_changes = {}
        self.tiles_currently_in_normal_view = {}
        self.tiles_currently_in_dim_view = {}
        for map_section_name in self.game.map_section_names:
            self.tiles_with_view_changes[map_section_name] = set()
            self.tiles_currently_in_normal_view[map_section_name] = set()
            self.tiles_currently_in_dim_view[map_section_name] = set()
        
        ev = RefreshAllSpritesEvent()
        queue.put(ev)

        ev = SwitchToEncounterModeEvent()
        queue.put(ev)

        '''
        # alternative approach where all the map sections are loaded into memory
        
        self.MapDim = {}
        self.viewableSurfDim = {}
        self.MapTL = {}
        self.mapInMapViewPortRect = {}
        self.preZoomedRect = {}
        self.mapOSDim = {}
        self.mapPixDim = {}
        self.maxtopleft = {}    
        
        self.brightTerrain = {}
        self.dimTerrain = {}        
        self.viewedTerrain = {}    
        
        self.miniMapTerrain = {}      
        self.dimminiMapTerrain = {}  
        self.viewedminiMapTerrain = {}
        self.miniMapAll = {}
        
        self.minimapTL = {}   
        self.minimapDim = {}
        self.MMMapConvFactor = {}
        self.mapCoordsForMMPixels = {}
        self.MMPixConvFactor = {} 
        self.minibox = {}           
        

        for sname,sdata in map.iteritems():      
            self.MapDim[sname] = sdata['dim']
            
            self.viewableSurfDim[sname] = []
            self.MapTL[sname] = []
            self.mapInMapViewPortRect[sname] = []
            self.preZoomedRect[sname] = []
            self.mapOSDim[sname] = []
            self.mapPixDim[sname] = []
            self.maxtopleft[sname] = []    
            #the largest value that the top left corner of the map in the mapViewPort
            #is allowed to have.  Otherwise, mapRect will move too far down and/or to the right.
            
#            self.elevmap = event.map.elevmap
            
            for i, zf in enumerate(zoomfactors):
                self.mapPixDim[sname].append( (int(round(self.tps[i]*self.MapDim[sname][0])), int(round(self.tps[i]*self.MapDim[sname][1])) ) )
                viewableSurfDim,TLPoint,mapOSDim = self.calcMapEdgeEffects(self.mapPixDim[sname][i],self.mapViewPortDim)
                self.viewableSurfDim[sname].append(viewableSurfDim)
                self.MapTL[sname].append(TLPoint)
                self.mapOSDim[sname].append(mapOSDim)
                self.mapInMapViewPortRect[sname].append(pygame.Rect(TLPoint[0],TLPoint[1]+toppanel_height,mapOSDim[0],mapOSDim[1]))
                self.preZoomedRect[sname].append( pygame.Rect(0,0,int(round(mapOSDim[0]/zf)), int(round(mapOSDim[1]/zf)) ) )
    
                if zf == 1.0:
                    self.brightTerrain[sname] = pygame.Surface(self.mapPixDim[sname][i]).convert()
                    for x in range(self.MapDim[sname][0]):
                        for y in range(self.MapDim[sname][1]):
                            spec = sdata[(x,y)]
                            partspec = (spec[0], spec[1])
                            sourcetile = self.maptile_surfdict[partspec]
                            self.brightTerrain[sname].blit(sourcetile,(x*tilepixsize,y*tilepixsize))
                        
            
                    dimness = pygame.Surface( viewableSurfDim[sname] )
                    dimness.fill((0,0,0))
                    dimness.set_alpha(127)
                
                    self.dimTerrain[sname] = self.brightTerrain[sname].copy().convert()
                    self.dimTerrain[sname].blit(dimness,(0,0))
                    self.viewedTerrain[sname] = self.dimTerrain.copy().convert()
                    
                    self.defaultzoomlevel = i
                                                        
                self.maxtopleft[sname].append( (self.viewableSurfDim[sname][i][0]-self.mapViewPortDim[0], self.viewableSurfDim[sname][i][1]-self.mapViewPortDim[1]) )
                
                                                        
            del dimness
            
            # build minimap terrain
            
            self.miniMapTerrain[sname] = pygame.Surface(self.minimapViewPortDim).convert()
            
            edgefrac = (max(self.MapDim[sname]) - min(self.MapDim[sname]))/(2.0*max(self.MapDim[sname]))
            if self.MapDim[sname][0] < self.MapDim[sname][1]:
                self.minimapTL[xname] = (int(round( edgefrac*self.minimapViewPortDim[0] )), 0)
            else:
                self.minimapTL[sname] = (0, int(round( edgefrac*self.minimapViewPortDim[1] )))
                
            self.minimapDim[sname] = ( int(self.minimapViewPortDim[0] - 2.0*self.minimapTL[sname][0]), int(self.minimapViewPortDim[1] - 2.0*self.minimapTL[sname][1]))
    
            self.MMMapConvFactor[sname] = float(max(self.minimapDim[sname])) / max(self.MapDim[sname])
            self.mapCoordsForMMPixels[sname] = {}
            for i in range(self.minimapDim[sname][0]):
                mmx = int(floor(i/self.MMMapConvFactor[sname]))
                for j in range(self.minimapDim[sname][1]):
                    mmy = int(floor(j/self.MMMapConvFactor[sname]))
                    spec = sdata[(mmx,mmy)]
                    partspec = (spec[0], spec[1])
                    mmbrightcolor = minimapcolors[partspec]
                    
                    self.miniMapTerrain[sname].set_at((i+self.minimapTL[sname][0],j+self.minimapTL[sname][1]),mmbrightcolor)
                    
                    if (mmx,mmy) in self.mapCoordsForMMPixels[sname]:
                        self.mapCoordsForMMPixels[sname][(mmx,mmy)].append((i,j))
                    else:
                        self.mapCoordsForMMPixels[sname][(mmx,mmy)] = [(i,j)]
                    
            dimness = pygame.Surface(self.minimapViewPortDim)
            dimness.fill((0,0,0))
            dimness.set_alpha(127)
            
            self.dimminiMapTerrain[sname] = self.miniMapTerrain[sname].copy().convert()
            self.dimminiMapTerrain[sname].blit(dimness,(0,0))
            self.viewedminiMapTerrain[sname] = self.dimminiMapTerrain[sname].copy().convert()
    
            self.miniMapAll[sname] = self.dimminiMapTerrain[sname].copy()
    
    
            self.MMPixConvFactor[sname] = [] 
            self.minibox[sname] = []           
            for i in range(self.numzooms):
                self.MMPixConvFactor[sname].append(float(self.minimapDim[sname][0]) / self.mapPixDim[sname][i][0])
                
                self.zoomlevel = i
                TLcoord = self.convertVSPixToMiniMapVSPix( (0, 0) )
                BRcoord = self.convertVSPixToMiniMapVSPix( self.mapViewPortDim )
                lbox = TLcoord[0]
                tbox = TLcoord[1]
                wbox = BRcoord[0]-TLcoord[0]
                hbox = BRcoord[1]-TLcoord[1]
                self.minibox[sname].append(pygame.Rect(lbox,tbox,wbox,hbox))
        
        '''
        
    def setMapToMapsection(self, sname):
        
        mapsec = self.map[sname]
        mapdim = mapsec['dim']
        self.tiles_known = set()
#        self.viewing_map_section = sname
#        self.game.mapsectionname = sname
        self.game.mapdim = mapdim
        
        self.MapDim = mapdim
        
        self.viewableSurfDim = []
        self.MapTL = []
        self.mapInMapViewPortRect = []
        self.preZoomedRect = []

        self.mapOSDim = []
        self.mapPixDim = []
        self.maxtopleft = []    
        ''' the largest value that the top left corner of the map in the mapViewPort
        is allowed to have.  Otherwise, mapRect will move too far down and/or to the right.'''
        
        for i, zf in enumerate(zoomfactors):
            self.mapPixDim.append( (int(round(self.tps[i]*mapdim[0])), int(round(self.tps[i]*mapdim[1])) ) )
            viewableSurfDim,TLPoint,mapOSDim = self.calcMapEdgeEffects(self.mapPixDim[i],self.mapViewPortDim)
            self.viewableSurfDim.append(viewableSurfDim)
            self.MapTL.append(TLPoint)
            self.mapOSDim.append(mapOSDim)
            self.mapInMapViewPortRect.append(pygame.Rect(TLPoint[0],TLPoint[1]+toppanel_height,mapOSDim[0],mapOSDim[1]))
            self.preZoomedRect.append( pygame.Rect(0,0,int(round(mapOSDim[0]/zf)), int(round(mapOSDim[1]/zf)) ) )

            if zf == 1.0:
                self.brightTerrain = pygame.Surface(self.mapPixDim[i]).convert()
                for x in range(mapdim[0]):
                    for y in range(mapdim[1]):
                        spec = mapsec[(x,y)]    # spec = (type, subtype, height) of terrain
                        partspec = (spec[0], spec[1])
                        sourcetile = random.choice(self.maptile_surfdict[partspec])
                        self.brightTerrain.blit(sourcetile,(x*tilepixsize,y*tilepixsize))
                    
        
                dimness = pygame.Surface( viewableSurfDim )
                dimness.fill((0,0,0))
                dimness.set_alpha(127)
            
                self.dimTerrain = self.brightTerrain.copy().convert()
                self.dimTerrain.blit(dimness,(0,0))
                self.viewedTerrain = self.dimTerrain.copy().convert()
                
                self.knownTerrain = self.dimTerrain.copy().convert()
                dimness.set_alpha(256)
                self.knownTerrain.blit(dimness,(0,0))
                
                for map_pos in self.game.map_data[sname]['known tiles']:
                    tempsurf = pygame.Surface( (self.tps[i],self.tps[i]) )
                    tempsurf = tempsurf.convert()
                    tilerect = pygame.Rect( 0,0,self.tps[i],self.tps[i] )
                    blitpos = self.convertMapPosToTLViewedTerrainPos(map_pos, True)
                    tilerect.topleft = blitpos
                    tempsurf.blit(self.dimTerrain,(0,0),tilerect)
                    self.knownTerrain.blit(tempsurf,blitpos)
                
                
                self.defaultzoomlevel = i
                                                    
            self.maxtopleft.append( (self.viewableSurfDim[i][0]-self.mapViewPortDim[0], self.viewableSurfDim[i][1]-self.mapViewPortDim[1]) )
            
                                                    
        del dimness
        
        # build minimap terrain
        
        self.miniMapTerrain = pygame.Surface(self.minimapViewPortDim).convert()
        
        edgefrac = (max(mapdim) - min(mapdim))/(2.0*max(mapdim))
        if mapdim[0] < mapdim[1]:
            self.minimapTL = (int(round( edgefrac*self.minimapViewPortDim[0] )), 0)
        else:
            self.minimapTL = (0, int(round( edgefrac*self.minimapViewPortDim[1] )))
            
        self.minimapDim = ( int(self.minimapViewPortDim[0] - 2.0*self.minimapTL[0]), int(self.minimapViewPortDim[1] - 2.0*self.minimapTL[1]))

        self.MMMapConvFactor = float(max(self.minimapDim)) / max(mapdim)
        self.mapCoordsForMMPixels = {}
        for i in range(self.minimapDim[0]):
            mmx = int(floor(i/self.MMMapConvFactor))
            for j in range(self.minimapDim[1]):
                mmy = int(floor(j/self.MMMapConvFactor))
                spec = mapsec[(mmx,mmy)]
                partspec = (spec[0], spec[1])
                mmbrightcolor = minimapcolors[partspec]
                
                self.miniMapTerrain.set_at((i+self.minimapTL[0],j+self.minimapTL[1]),mmbrightcolor)
                
                if (mmx,mmy) in self.mapCoordsForMMPixels:
                    self.mapCoordsForMMPixels[(mmx,mmy)].append((i,j))
                else:
                    self.mapCoordsForMMPixels[(mmx,mmy)] = [(i,j)]
                
        dimness = pygame.Surface(self.minimapViewPortDim)
        dimness.fill((0,0,0))
        dimness.set_alpha(127)
        
        self.dimminiMapTerrain = self.miniMapTerrain.copy().convert()
        self.dimminiMapTerrain.blit(dimness,(0,0))
        self.viewedminiMapTerrain = self.dimminiMapTerrain.copy().convert()

        self.miniMapAll = self.dimminiMapTerrain.copy()


        self.MMPixConvFactor = [] 
        self.minibox = []           
        for i in range(self.numzooms):
            self.MMPixConvFactor.append(float(self.minimapDim[0]) / self.mapPixDim[i][0])
            
            self.zoomlevel = i
            TLcoord = self.convertVSPixToMiniMapVSPix( (0, 0) )
            BRcoord = self.convertVSPixToMiniMapVSPix( self.mapViewPortDim )
            lbox = TLcoord[0]
            tbox = TLcoord[1]
            wbox = BRcoord[0]-TLcoord[0]
            hbox = BRcoord[1]-TLcoord[1]
            self.minibox.append(pygame.Rect(lbox,tbox,wbox,hbox))
            
        self.zoomlevel = self.defaultzoomlevel
        self.oldzoomlevel = self.defaultzoomlevel
                
    def createTileViewMasks(self):
        self.tileViewMaskDict = {}
        
        for i in range(128):
            tsurf = pygame.Surface( (tilepixsize,tilepixsize) )
            tsurf.fill((0,0,0))
            tsurf.set_alpha(i)
            self.tileViewMaskDict[i] = tsurf
                
    def create_allowed_tile_mask(self):
        tsurf = pygame.Surface( (tilepixsize,tilepixsize) )
        tsurf.fill((0,240,0))
        tsurf.set_alpha(30)
        self.allowed_tile_mask = tsurf
                
    def create_effect_area_mask(self):
        tsurf = pygame.Surface( (tilepixsize,tilepixsize) )
        tsurf.fill((200,200,0))
        tsurf.set_alpha(40)
        self.effect_area_mask = tsurf
                
    def updateSelectedUnitsInSelectionWindow(self):     # not used atm
        
        if self.selectionWindowSpritesLower:
            for sp in self.selectionWindowSpritesLower:
                loc = sp.rect.topleft
                self.selectionWindow.blit(self.selectionwinBackground,loc,sp.rect)
        self.selectionWindowSpritesLower.empty()
        
        oldSWselectedobj = self.SWselectedObj
        oldSWpursuedobj = self.SWpursuedObj
        for sp in self.selectionWindowSpritesUpper.sprites():
            if sp == self.selectedObj:
                loc = sp.medsprite.rect.topleft
                self.selectionWindow.blit(self.selectionwinBackground,loc,sp.medsprite.rect)
                self.selectionWindow.blit(sp.medsprite.imagesel,loc)
                self.SWselectedObj = sp
                if sp.type == 'unitgroup':
                    group = sp.object
                    for unum, uid in enumerate(group.members):
                        u = self.game.objectIdDict[uid]
                        unitmedsp = self.uv.AssembleMedSprite(u)
                        subloc = (unum*17+1,36)
                        unitmedsp.rect.topleft = subloc
                        self.selectionWindowSpritesLower.add(unitmedsp)
                        if self.subselectedLoc and unitmedsp.rect.collidepoint(self.subselectedLoc):
                            self.selectionWindow.blit(unitmedsp.imagesel,subloc)
                        else:
                            self.selectionWindow.blit(unitmedsp.imageus,subloc)
                        
#                    for gnum,gmsp in enumerate(sp.groupsprites):
#                        gmloc = (gnum*17+1,36)
#                        gmsp.medsprite.rect.topleft = gmloc
#                        self.selectionWindowSpritesLower.add(gmsp)
#                        if gmsp == self.subselectedObj:
#                            self.selectionWindow.blit(gmsp.medsprite.imagesel,gmloc)
#                        else:
#                            self.selectionWindow.blit(gmsp.medsprite.imageus,gmloc)
            elif sp == oldSWselectedobj:
                loc = sp.medsprite.rect.topleft
                self.selectionWindow.blit(self.selectionwinBackground,loc,sp.medsprite.rect)
                self.selectionWindow.blit(sp.medsprite.imageus,loc)
                
            elif sp == self.pursuedObj:
                loc = sp.medsprite.rect.topleft
                self.selectionWindow.blit(self.selectionwinBackground,loc,sp.medsprite.rect)
                self.selectionWindow.blit(sp.medsprite.imageselPursued,loc)
                self.SWpursuedObj = sp
                
            elif sp == oldSWpursuedobj:
                loc = sp.medsprite.rect.topleft
                self.selectionWindow.blit(self.selectionwinBackground,loc,sp.medsprite.rect)
                self.selectionWindow.blit(sp.medsprite.imageus,loc)
                
        self.view_refresh_needed = True
        print 'mainview, vrn2'
                
                
    def updateSelectionWindow(self):
        self.selectionWindow.blit(self.selectionwinBackground,(0,0))
        
        if self.selectedSprite:
            sS = self.selectedSprite
            obj = sS.object
            if obj.objtype == 'playerchar':
                x = 1
                y = 1
                colortag = fontdefault22.render(obj.name, True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                y += self.font22_linesize
                y1 = y
                colortag = fontdefault20.render('Str: '+str(obj.str), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                y += self.font20_linesize
                colortag = fontdefault20.render('Dex: '+str(obj.dex), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                y += self.font20_linesize
                colortag = fontdefault20.render('Int: '+str(obj.int), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                x += 80
                y = y1
                colortag = fontdefault20.render('Con: '+str(obj.con), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                y += self.font20_linesize
                colortag = fontdefault20.render('Wis: '+str(obj.wis), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                y += self.font20_linesize
                colortag = fontdefault20.render('Cha: '+str(obj.cha), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y))
                x += 80
                colortag = fontdefault20.render('HP: '+str(obj.find_current_hit_points())+'/'+str(obj.max_hit_points), True, (255,255,255))
                self.selectionWindow.blit(colortag,(x,y1))
                
                self.view_refresh_needed = True
                print 'mainview, vrn3'
        
#            for iiw in range(self.num_iw_fields):
#                if self.iwfield[iiw] != self.oldiwfield[iiw]:
#                
#                    # create new surface with text
#                    colortag = fontdefault14.render(self.iwfield[iiw], 1, (255,255,255),infowindowbackgroundcolor)
#
#                    # clear previous data
#                    self.window.blit(self.iwfieldbgsurf,self.iwfieldrect[iiw])
#
#                    # put new surfaces onto window surface
#                    self.window.blit(colortag,self.iwfieldrect[iiw])
#
#                    dirtyrects.append(self.iwfieldrect[iiw])                         
#
#            if dirtyrects:
#                pygame.display.update(dirtyrects)
        
        
#        if self.selectedSprites:
#            
#            for num,sp in enumerate(reversed(self.selectedSprites)):
#                loc = (num*17+1,2)
#                sp.medsprite.rect.topleft = loc
#                self.selectionWindow.blit(sp.medsprite.imageus,loc)
#            self.view_refresh_needed = True
                
    def selectionWindowLeftClickEvent(self, pos, shiftkeypressed, pursuemode):
        pass
        swpos = self.convertWholeViewPortPixToSelectionWindowPix(pos)
        spriteUnderClick = None
        if self.selectedSprites:
            for sp in self.selectedSprites:
                if sp.medsprite.rect.collidepoint(swpos):
                    spriteUnderClick = sp
                    break

        if spriteUnderClick:
            if not pursuemode:
                if shiftkeypressed:
                    spritelist = list(self.selectedSprites)
                    spritelist.remove(spriteUnderClick)
                else:
                    spritelist = []
                    spritelist.append(spriteUnderClick)
                ev = SpritesSelectedEvent(spritelist)
                queue.put(ev)
                    
            else:
                ev = PursuedUnitSelectedEvent(spriteUnderClick)
                queue.put(ev)
                
    def selectionWindowRightClickEvent(self, pos, keymods, pursuemode):
        if pursuemode:
            swpos = self.convertWholeViewPortPixToSelectionWindowPix(pos)
            spriteUnderClick = None
            if self.selectedSprites:
                for sp in self.selectedSprites:
                    if sp.medsprite.rect.collidepoint(swpos):
                        spriteUnderClick = sp
                        break
                    
            if spriteUnderClick:
                topobj = None
                if hasattr(spriteUnderClick,'object') and spriteUnderClick.type == 'unit':
                    topobj = spriteUnderClick.object
    
                for sp in self.selectedSpritesBackup:
                    if hasattr(sp,'object') and sp.type == 'unit':
                        if sp.object.nation == self.game.mynation:
                            ev = RequestTargetEvent(sp.object, topobj.id)
                            queue.put(ev)
                                
                ev = ChangePursueMode()
                queue.put(ev)
                    
    def mapLeftClickEvent(self, pos, shiftkeypressed):  
        # only own playerchars can ever be selected              
        # left clicking on empty tile deselects
        
        clickpos = self.convertWholeViewPortPixToVSPix(pos)
        spritesUnderClick = self.allMapSprites.get_sprites_at(clickpos)
        own_char_clicked = False
        for spr in spritesUnderClick:
            if hasattr(spr,'type'):
                if spr.type == 'playerchar':
                    char = spr.object
                    if self.game.myprofname == self.game.charsplayer[char.name]:
                        own_char_clicked = True
                        ev = SpriteSelectedEvent(spr,True)
                        queue.put(ev)
                        break
        if not own_char_clicked:
            self.use_effect_area_func = False
            self.set_effect_area_tiles(None)
            ev = SpriteSelectedEvent(None, False)
            queue.put(ev)
            
            
#        num_under_click = len(spritesUnderClick)
#        if num_under_click == 0:
#            sp = None
#            self.left_click_sprite_list = []
#        elif num_under_click == 1:
#            sp = spritesUnderClick[0]
#            self.left_click_sprite_list = [sp]
#        else:
#            if self.selectedSprite == spritesUnderClick[-1]:
#                for spr in self.left_click_sprite_list:
#                    if spr not in spritesUnderClick:
#                        self.left_click_sprite_list.remove(spr)
#                for spr in reversed(spritesUnderClick):
#                    if spr not in self.left_click_sprite_list:
#                        self.left_click_sprite_list.append(spr)
#                oldsp = self.left_click_sprite_list.remove(self.selectedSprite)
#                self.left_click_sprite_list.append(oldsp)
#                sp = self.left_click_sprite_list[0]
#            else:
#                sp = spritesUnderClick[-1]
#                self.left_click_sprite_list = reversed(spritesUnderClick)
#            
#        if sp != self.selectedSprite:
#            ev = SpriteSelectedEvent(sp)
#            queue.put(ev)

    def mapRightClickEvent(self, pos, keymods, target_mode):
        # -when not in target mode and char not selected:
        #   -right clicking on empty tile brings up terrain info
        #   -right clicking on tile with one sprite and that sprite is 
        #    own char selects char and brings up extensive menu
        #   -right clicking on tile with one sprite that isn't own char
        #    brings up info about that obj
        #   -right clicking on tile with multiple sprites brings up choice menu
        #    and making a choice brings up either info (if not own playerchar)
        #    or extensive menu if own playerchar
        # -when not in target mode and char selected and shift not pressed:
        #   -right clicking on empty tile orders move to that tile, if allowed
        #    otherwise does nothing
        #   -right clicking on tile with one sprite and that sprite is 
        #    own char selects char and brings up extensive menu
        #   -right clicking on tile with one sprite that isn't own char
        #    brings up info about that obj
        #   -right clicking on tile with multiple sprites bring up choice menu
        #    and making a choice brings up either info (if not own playerchar)
        #    or extensive menu if own playerchar
        # -when not in target mode and char selected and shift pressed:
        #   -right clicking on any tile orders move to that tile, if allowed
        #    otherwise does nothing
        # -when not in target mode and ctrl pressed:
        #   -right clicking on any tile brings up terrain info
        
        # -if in targetting mode and more than one valid target is at mappos, then
        #  automatically bring up choosable list of valid targets with right click (or
        #  maybe use exact same logic as right click (and ctrl right click) when some 
        #  object is selected, except only valid targets are displayed in choice list, and 
        #  when target is chosen no further menu pops up (usually))
        # -hovering for a sec over a tile brings up list of objects at that mappos, (but not
        #  a choosable list) somewhat like a right click menu, but it disappears as soon as 
        #  mouse moves away from mappos
        
        old_use_effect_area_func = self.use_effect_area_func 
        self.use_effect_area_func = False
        self.set_effect_area_tiles(None)
#        self.set_effect_area_func(None)
                        
        vspos = self.convertWholeViewPortPixToVSPix(pos)
        mappos = self.convertWholeViewPortPixToMapPos(pos)
        
        ctrl_pressed = keymods & KMOD_CTRL
        shift_pressed = keymods & KMOD_SHIFT
        
#        self.hover_sprite_dict['playerchar'] = s
        
        if target_mode:     # in target_mode, self.num_sprites_under_mouse and self.hover_sprite_list
                            # will only list allowed targets, not all the sprites that might be at mappos
            if self.num_sprites_under_mouse == 0:
                if mappos in self.allowed_tiles_overlay:
                    ev = TargetChosenEvent(mappos)
                    queue.put(ev)
                else:
                    self.use_effect_area_func = old_use_effect_area_func
#                    self.set_effect_area_tiles(mappos)
                    
            elif self.num_sprites_under_mouse == 1:
                ev = TargetChosenEvent(self.hover_sprite_list[0].object)
                queue.put(ev)
            else:
                ev = RaiseSpriteChoiceMenuEvent(self.hover_sprite_list, TargetChosenEvent, pos)
                queue.put(ev)
            
        else:
            if ctrl_pressed:
                ev = TerrainRightClickEvent(mappos)
                queue.put(ev)
                
            else:
                if self.selectedSprite and (self.num_sprites_under_mouse == 0 or shift_pressed):
                    moveable_sprite = self.uv.evalSpriteForMove(self.selectedSprite, mappos)
                    if moveable_sprite:
                        ev = MoveOrder_Game(moveable_sprite.object, mappos)
                        queue.put(ev)
                elif self.num_sprites_under_mouse == 0:
                    ev = TerrainRightClickEvent(mappos)
                    queue.put(ev)
                elif self.num_sprites_under_mouse == 1:
                    spr = self.hover_sprite_list[0]
                    if spr.type == 'playerchar':
                        char = spr.object
                        if self.game.myprofname == self.game.charsplayer[char.name]:
                            ev = SpriteSelectedEvent(spr, True)
                            queue.put(ev)
                        if not (self.game.move_mode == 'phased' and char.before_order_decisions):
                            ev = SpriteRightClickEvent(spr, pos)
                            queue.put(ev)
                    else:
                        ev = SpriteRightClickEvent(spr, pos)
                        queue.put(ev)
                else:
                    if self.selectedSprite in self.hover_sprite_list:
                        ev = SpriteRightClickEvent(self.selectedSprite, pos)
                        queue.put(ev)
                    else:
                        ev = RaiseSpriteChoiceMenuEvent(self.hover_sprite_list, SpriteRightClickEvent, pos)
                        queue.put(ev)
#                    if not shift_pressed:
#                        for spr in self.hover_sprite_list:
#                            if spr.type == 'playerchar':
#                                char = spr.object
#                                if self.game.myprofname == self.game.charsplayer[char.name]:
#                                    ev = SpriteSelectedEvent(spr)
#                                    queue.put(ev)
#                                    ev = SpriteRightClickEvent(spr, pos)
#                                    queue.put(ev)
#                                    break
#                    else:
#                        ev = RaiseSpriteChoiceMenuEvent(self.hover_sprite_list, SpriteRightClickEvent, pos)
#                        queue.put(ev)
                            
#            else:
#                if self.num_sprites_under_mouse == 0:
#                    ev = TerrainRightClickEvent(mappos)
#                    queue.put(ev)
#                elif self.num_sprites_under_mouse == 1:
#                    sp = self.hover_sprite_list[0]
##                    ev = SpriteSelectedEvent(sp)
##                    queue.put(ev)
#                    ev = SpriteRightClickEvent(sp, pos, None)
#                    queue.put(ev)
#                else:
#                    ev = RaiseSpriteChoiceMenuEvent(self.hover_sprite_list, SpriteRightClickEvent, pos, None)
#                    queue.put(ev)
            
    def miniMapRightClickEvent(self, pos, pursuemode):
        mappos = self.convertMiniMapVSPixToMapPos( (pos[0] - self.minimaprect.left , pos[1] - self.minimaprect.top) )
        refreshSelection = False
        
#        if hasattr(sp,'object') and sp.type == 'unit':
#            if sp.object.nation == self.game.mynation:
#                ev = MoveOrder_Game(sp.object, mappos)
#                queue.put(ev)
                    
    def buildSpriteListsUnderClick(self,vspos):
        # build a list of map positions for sprites under click
        # then build a list of sprite at each map position
        self.unitMapPosListForSpritesUnderClick = []
        self.spriteListAtEachMapPosUnderClick = []
        allSpritesUnderClick = self.allMapSprites.get_sprites_at(vspos)
        topsprite = None
        topsprite_mappos = None
        for s in allSpritesUnderClick:      # start with sprites on bottom
            mappos = None
            if hasattr(s,'type'):
                if s.type == "unit" or s.type == "city" or s.type == "unitgroup":   
                    # don't care about view circles, order lines, order sprites
                    mappos = s.object.pos
                
            if mappos:
                if mappos not in self.unitMapPosListForSpritesUnderClick:
                    self.unitMapPosListForSpritesUnderClick.append(mappos)
                    self.spriteListAtEachMapPosUnderClick.append([])
                mapposidx = self.unitMapPosListForSpritesUnderClick.index(mappos)
                self.spriteListAtEachMapPosUnderClick[mapposidx].append(s)
                topsprite = s
                topsprite_mappos = mappos
                
        return topsprite, topsprite_mappos


    def clear_hover_sprites(self):        
        self.hover_sprite_dict['playerchar'] = None
        self.hover_sprite_dict['monster'] = None
        self.hover_sprite_dict['carried_item'] = []
        self.hover_sprite_dict['fixed_item'] = []
        self.hover_sprite_dict['trap'] = None
        self.hover_sprite_dict['other_mobj'] = None
        self.hover_sprite_list = []
        
    def create_hover_popup(self, mousepos):

        self.pguctrl.hide_primary_floating_menu()
        self.popup_floating_rect = None
        
        data = deepcopy(self.default_hover_popup_data)
        data['default']['font'] = self.def_hover_popup_font
        
        num_menu_items = 0
        above_line = False
        show = False
        if self.hover_sprite_dict['playerchar']:
            num_menu_items += 1
            above_line = True
            show = True
            obj = self.hover_sprite_dict['playerchar'].object
            data['section'][1][num_menu_items] = {}
            data['section'][1][num_menu_items]['string'] = obj.name
#            data['section'][1][self.num_menu_items]['function'] = self.show_object_info
        if self.hover_sprite_dict['monster']:
            num_menu_items += 1
            above_line = True
            show = True
            obj = self.hover_sprite_dict['monster'].object
            mon_str = ''
            if obj.display_name:
                mon_str += obj.display_name + ' '
            mon_str += ', ' + obj.species
            data['section'][1][num_menu_items] = {}
            data['section'][1][num_menu_items]['string'] = mon_str
        if self.hover_sprite_dict['carried_item']:
            for item in self.hover_sprite_dict['carried_item']:
                num_menu_items += 1
                above_line = True
                show = True
                obj = item.object
                item_str = ''
                if obj.name:
                    item_str += obj.display_name
                for otype in obj.type:
                    item_str += ' ' + otype
                for ostype in obj.subtype:
                    item_str += ' ' + ostype
                data['section'][1][num_menu_items] = {}
                data['section'][1][num_menu_items]['string'] = item_str
                
        if above_line:
            data['section']['divider'] = {}
            section_num = 2
        else:
            section_num = 1

        if self.hover_sprite_dict['fixed_item']:
            for item in self.hover_sprite_dict['fixed_item']:
                num_menu_items += 1
                show = True
                obj = item.object
                item_str = ''
                if obj.name:
                    item_str += obj.name + ' '
                item_str += obj.type
                if obj.subtype:
                    item_str += ' ' + obj.subtype
                data['section'][section_num][num_menu_items] = {}
                data['section'][section_num][num_menu_items]['string'] = item_str
        if self.hover_sprite_dict['trap']:
            num_menu_items += 1
            show = True
            obj = self.hover_sprite_dict['trap'].object
            trap_str = ''
            if obj.name:
                trap_str += obj.name + ' '
            trap_str += obj.type
            if obj.subtype:
                trap_str += ' ' + obj.subtype
            data['section'][section_num][num_menu_items] = {}
            data['section'][section_num][num_menu_items]['string'] = trap_str
        if self.hover_sprite_dict['other_mobj']:
            num_menu_items += 1
            show = True
            obj = self.hover_sprite_dict['other_mobj'].object
            oth_str = ''
            if obj.name:
                oth_str += obj.name + ' '
            oth_str += obj.type
            if obj.subtype:
                oth_str += ' ' + obj.subtype
            data['section'][section_num][num_menu_items] = {}
            data['section'][section_num][num_menu_items]['string'] = oth_str
                
        if show:
            puf = self.pguctrl.create_primary_floating_menu(data, (mousepos, self.mapViewPortRect))
            self.popup_floating_rect = puf.rect
    
    def mouseOver(self, mousepos):
        
        if not self.mouseOverEventLocked:

#            Mouse hovering over main map
            if self.mapInMapViewPortRect[self.zoomlevel].collidepoint(mousepos):
                if not self.primary_floating_menu_rect:
                    vspos = self.convertWholeViewPortPixToVSPix(mousepos)
                    mappos = self.convertVSPixToMapPos(vspos)
                    if mappos != self.old_map_pos_hover or self.target_mode != self.old_target_mode:
                        self.old_map_pos_hover = mappos
                        self.old_target_mode = self.target_mode
                        self.num_sprites_under_mouse = 0
                        self.clear_hover_sprites()
                        if self.target_mode:
                            sprites_under_click = self.targetting_mode_sprites_under_click.get_sprites_at(vspos)
                        else:
                            sprites_under_click = self.allMapSprites.get_sprites_at(vspos)
                        for s in sprites_under_click:      
                            if hasattr(s,'type'):
                                self.num_sprites_under_mouse += 1
                                self.hover_sprite_list.append(s)
                                if s.type == "playerchar":
                                    self.hover_sprite_dict['playerchar'] = s
                                elif s.type == "monster":
                                    self.hover_sprite_dict['monster'] = s
                                elif s.type == "carried_item":
                                    self.hover_sprite_dict['carried_item'].append(s)
                                elif s.type == "fixed_item":
                                    self.hover_sprite_dict['fixed_item'].append(s)
                                elif s.type == "trap":
                                    self.hover_sprite_dict['trap'] = s
                                elif s.type == "other_mobj":
                                    self.hover_sprite_dict['other_mobj'] = s
                                    
                        self.create_hover_popup(mousepos)
                
                        if mappos in self.allowed_tiles_overlay:
                            self.set_effect_area_tiles(mappos)
                        else:
                            self.set_effect_area_tiles(None)
                        
#            Mouse hovering over selection window units
            elif self.selectionwinrect.collidepoint(mousepos):
                self.old_map_pos_hover = None
            
            else:       # nothing interesting under mouse, clear mouseover window
                self.old_map_pos_hover = None
            
      
    def drawSelectRect(self, pos1, pos2):
        if self.selectRectSprite:
            self.allMapSprites.remove(self.selectRectSprite)
        if pos1:
            if self.selectRectSprite:
                self.allMapSprites.remove(self.selectRectSprite)
            vsstartpos = self.convertWholeViewPortPixToVSPix(pos1)
            vsendpos = self.convertWholeViewPortPixToVSPix(pos2)
            newSprite = spritevisuals.createRectSprite((255,255,255), vsstartpos, vsendpos)
            newSprite._layer = self.selectrectlayer   
            self.allMapSprites.add(newSprite)
            self.selectRectSprite = newSprite
    
        self.view_refresh_needed = True    
        print 'mainview, vrn4'
        
    def make_tiles_known(self, dict_of_new_knowns):
        if self.viewing_map_section in dict_of_new_knowns:
            new_tiles = dict_of_new_knowns[self.viewing_map_section]
            for map_pos in new_tiles:
                if map_pos not in self.tiles_known:
                    self.tiles_known.add(map_pos)
                    tempsurf = pygame.Surface( (tilepixsize,tilepixsize) )
                    tempsurf = tempsurf.convert()
                    tilerect = pygame.Rect( 0,0,tilepixsize,tilepixsize )
                    blitpos = self.convertMapPosToTLViewedTerrainPos(map_pos, True)
                    tilerect.topleft = blitpos
                    tempsurf.blit(self.dimTerrain,(0,0),tilerect)
                    self.knownTerrain.blit(tempsurf,blitpos)

    def put_viewed_tiles_aux(self, tempsurf, tilerect, mappos, view_intens, maxdispviewlevel):
        tempsurf.blit(self.brightTerrain,(0,0),tilerect)
        if TERRAIN_BRIGHTNESS_INDICATES_LIGHT_LEVEL:
            totalviewlevel = self.game.map_data[self.viewing_map_section]['light'][mappos]
        else:
            totalviewlevel = view_intens
#                totalviewlevel = self.game.tilesWithinView[self.viewing_map_section][mappos]
        dispviewlevel = int(round(min(127,totalviewlevel*127/maxdispviewlevel)))
        dimness = 127-dispviewlevel
        
        tempsurf.blit(self.tileViewMaskDict[dimness],(0,0))

#    def put_view_light(self, map_pos):
#        return self.game.map_data[self.viewing_map_section]['light'][map_pos]
#    
#    def put_view_2(self, map_pos):
#        return 2
#        
#    def put_view_1(self, map_pos):
#        return 1
    
    def putViewedTiles(self, doallviewedtiles):
        #self.allMapSprites.remove(self.viewedTileSprites)
#        zl = self.zoomlevel
        #vM = self.viewableMap[zl]
        print 'mainview', 'putting viewed tiles', doallviewedtiles, SHARED_SIGHT
        
        gT = self.brightTerrain
        tps = tilepixsize
        #n = self.game.mynation
        
        
        tempsurf = pygame.Surface( (tps,tps) )
        tempsurf = tempsurf.convert()
        tilerect = pygame.Rect( 0,0,tps,tps )
        
#        for mappos,vc in self.game.viewlevelChanges.iteritems():
#            if vc != 0:
#                if mappos in self.zvlChanges:
#                    self.zvlChanges[mappos] += vc
#                else:
#                    self.zvlChanges[mappos] = vc

        if TERRAIN_BRIGHTNESS_INDICATES_LIGHT_LEVEL:
            maxdispviewlevel = 13
        else:   # else terrain brightness indicates view level (normal or dim)
            maxdispviewlevel = 2
                
        self.tiles_currently_in_normal_view = set()
        self.tiles_currently_in_dim_view = set()
        if SHARED_SIGHT:
#            self.tiles_currently_in_normal_view = self.game.tiles_within_party_normal_view[self.viewing_map_section]
#            self.tiles_currently_in_dim_view = self.game.tiles_within_party_dim_view[self.viewing_map_section]
            view_utils.update_game_best_view_tile_sets(self.game, self.viewing_map_section)
            self.tiles_currently_in_normal_view = self.game.tiles_within_party_normal_view
            self.tiles_currently_in_dim_view = self.game.tiles_within_party_dim_view
        else:
            if self.selectedSprite:
                if hasattr(self.selectedSprite,'object'):
                    object = self.selectedSprite.object
                    if object.objtype == 'playerchar':
#                    object2 = self.game.objectIdDict[object1.id]    # to make sure we're using the object
                                                                    # active in the current self.game (selectedSprite
                                                                    # data isn't saved)
                        self.tiles_currently_in_normal_view = object.normal_viewed_tiles  
                        self.tiles_currently_in_dim_view = object.dim_viewed_tiles
        
        if doallviewedtiles:    
            
            self.viewedTerrain = self.knownTerrain.copy().convert()
            
            vT = self.viewedTerrain
        
            for mappos in self.tiles_currently_in_normal_view:
                blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                tilerect.topleft = blitpos
                self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,2,maxdispviewlevel)
                vT.blit(tempsurf,blitpos)

            for mappos in self.tiles_currently_in_dim_view:
                blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                tilerect.topleft = blitpos
                self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,1,maxdispviewlevel)
                vT.blit(tempsurf,blitpos)
                
            for mappos in self.allowed_tiles_overlay:
                blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                vT.blit(self.allowed_tile_mask, blitpos)
                
            for mappos in self.effect_area_overlay:
                blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                vT.blit(self.effect_area_mask, blitpos)

        else:       # not used atm
        
            vT = self.viewedTerrain
        
            #for mappos,vc in self.game.viewlevelChanges[self.game.myteam].iteritems():
            for mappos in self.game.viewlevelChanges[self.viewing_map_section]:
#                if vc != 0:
                    
                blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                tilerect.topleft = blitpos
                
                if mappos in self.game.tiles_within_party_normal_view[self.viewing_map_section]:
                    self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,2,maxdispviewlevel)
                elif mappos in self.game.tiles_within_party_dim_view[self.viewing_map_section]:
                    self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,1,maxdispviewlevel)
                else:
                    tempsurf.blit(self.dimTerrain,(0,0),tilerect)
                    
                if mappos in self.allowed_tiles_overlay:
                    tempsurf.blit(self.allowed_tile_mask,(0,0))
            
                vT.blit(tempsurf,blitpos)
                
            for mappos in self.allowed_tiles_overlay:
                if mappos not in self.game.viewlevelChanges[self.viewing_map_section]:
                    blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                    tilerect.topleft = blitpos
                    
                    if mappos in self.game.tiles_within_party_normal_view[self.viewing_map_section]:
                        self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,2,maxdispviewlevel)
                    elif mappos in self.game.tiles_within_party_dim_view[self.viewing_map_section]:
                        self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,1,maxdispviewlevel)
                    else:
                        tempsurf.blit(self.dimTerrain,(0,0),tilerect)
                        
                    tempsurf.blit(self.allowed_tile_mask,(0,0))
                    vT.blit(tempsurf, blitpos)
                    
            for mappos in self.tiles_now_not_allowed:
                
                if mappos not in self.game.viewlevelChanges[self.viewing_map_section]:
                    blitpos = self.convertMapPosToTLViewedTerrainPos(mappos, True)
                    tilerect.topleft = blitpos
                    
                    if mappos in self.game.tiles_within_party_normal_view[self.viewing_map_section]:
                        self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,2,maxdispviewlevel)
                    elif mappos in self.game.tiles_within_party_dim_view[self.viewing_map_section]:
                        self.put_viewed_tiles_aux(tempsurf,tilerect,mappos,1,maxdispviewlevel)
                    else:
                        tempsurf.blit(self.dimTerrain,(0,0),tilerect)
                        
                    vT.blit(tempsurf, blitpos)
                
                
                
                
                #if totalviewlevel == 0:
                    #del self.game.tilesWithinView[mappos]
                            
            for mappos in self.game.viewlevelChanges[self.viewing_map_section]:
#                if vc != 0:
                if mappos in self.mapCoordsForMMPixels:
                    if mappos in self.game.tiles_within_party_normal_view[self.viewing_map_section]:
                        if TERRAIN_BRIGHTNESS_INDICATES_LIGHT_LEVEL:
                            totalviewlevel = self.game.map_data[self.viewing_map_section]['light'][mappos]
                        else:
                            totalviewlevel = 2
                        dispviewlevel = int(round(min(127,totalviewlevel*127/maxdispviewlevel)))
                        dimness = float((129 + dispviewlevel)) / 256
                        
                        for mmpos in self.mapCoordsForMMPixels[mappos]:
                            brcolor = self.miniMapTerrain.get_at(mmpos)
                            
                            dimr = int(brcolor[0]*dimness)
                            dimg = int(brcolor[1]*dimness)
                            dimb = int(brcolor[2]*dimness)
                            self.viewedminiMapTerrain.set_at(mmpos,(dimr,dimg,dimb,255)) 
                    elif mappos in self.game.tiles_within_party_dim_view[self.viewing_map_section]:
                        if TERRAIN_BRIGHTNESS_INDICATES_LIGHT_LEVEL:
                            totalviewlevel = self.game.map_data[self.viewing_map_section]['light'][mappos]
                        else:
                            totalviewlevel = 1
                        dispviewlevel = int(round(min(127,totalviewlevel*127/maxdispviewlevel)))
                        dimness = float((129 + dispviewlevel)) / 256
                        
                        for mmpos in self.mapCoordsForMMPixels[mappos]:
                            brcolor = self.miniMapTerrain.get_at(mmpos)
                            
                            dimr = int(brcolor[0]*dimness)
                            dimg = int(brcolor[1]*dimness)
                            dimb = int(brcolor[2]*dimness)
                            self.viewedminiMapTerrain.set_at(mmpos,(dimr,dimg,dimb,255)) 

            
#        self.game.viewlevelChanges[self.viewing_map_section] = set()

    def set_allowed_moves_old(self, object):
        update_needed = False
        '''
        if object:
            if object.allowed_move_tiles != self.allowed_moves:
                update_needed = True
                self.allowed_moves = deepcopy(object.allowed_move_tiles)
        else:
            if self.allowed_moves != []:
                update_needed = True
                self.allowed_moves = []          
                
        if update_needed:
            eV = UpdateMap()
            queue.put(eV)
        '''

        if object:
            new_allowed_set = set(object.allowed_move_tiles)
        else:
            new_allowed_set = set()
        old_allowed_set = set(self.allowed_moves)
        tiles_now_not_allowed = old_allowed_set - new_allowed_set 
        self.tiles_now_not_allowed = tiles_now_not_allowed
        if tiles_now_not_allowed:
            update_needed = True
#            for pos in tiles_now_not_allowed:
#                self.game.viewlevelChanges[pos] = 0
            
        new_tiles_allowed = new_allowed_set - old_allowed_set
        if new_tiles_allowed:
            update_needed = True
#            for pos in new_tiles_allowed:
#                self.game.viewlevelChanges[pos] = 0
            
        if update_needed:
            if object:
                self.allowed_moves = deepcopy(object.allowed_move_tiles)
            else:
                self.allowed_moves = set()

            self.set_allowed_tiles_and_targets(self.allowed_moves, set())                          
#            self.set_allowed_tiles_overlay(self.allowed_moves)
            eV = UpdateMap()
            queue.put(eV)

    def set_allowed_moves(self, object):
        if object:
            if object.allowed_move_tiles != self.allowed_moves:
                self.allowed_moves = set(object.allowed_move_tiles)
                self.set_allowed_tiles_and_targets(object.allowed_move_tiles, set())                          
        elif self.allowed_moves:
            self.allowed_moves = set()
            self.set_allowed_tiles_and_targets(self.allowed_moves, set())                          

    def set_allowed_tiles_and_targets(self, tiles, targets):
        self.allowed_tiles_overlay = deepcopy(tiles)
#        self.allowed_target_sprites = set()
        self.targetting_mode_sprites_under_click.empty()
        for target in targets:
            sp = self.uv.GetObjectSprite(target,self.allMapSprites)
            if sp:
#                self.allowed_target_sprites.add(sp)
                self.allowed_tiles_overlay.add(target.pos)
                self.targetting_mode_sprites_under_click.add(sp)
            
    def set_allowed_move_tiles(self, tiles):
        self.allowed_tiles_overlay = deepcopy(tiles)
#        self.allowed_target_sprites = set()
            
    def set_allowed_target_tiles_and_objects(self, tiles, targets):
        self.allowed_tiles_overlay = deepcopy(tiles)
#        self.allowed_target_sprites = set()
        self.targetting_mode_sprites_under_click.empty()
        for target in targets:
            sp = self.uv.GetObjectSprite(target,self.allMapSprites)
            if sp:
#                self.allowed_target_sprites.add(sp)
                self.allowed_tiles_overlay.add(target.pos)
                self.targetting_mode_sprites_under_click.add(sp)
            
#    def set_allowed_tiles_overlay(self, new_tile_set):
#        self.allowed_tiles_overlay = deepcopy(new_tile_set)
#
#    def set_allowed_target_sprites(self, allowed_targets):
#        self.allowed_target_sprites = set()
#        self.allowed_tiles_overlay = set()
#        self.targetting_mode_sprites_under_click.empty()
#        for target in allowed_targets:
#            sp = self.uv.GetObjectSprite(target,self.allMapSprites)
#            if sp:
#                self.allowed_target_sprites.add(sp)
#                self.allowed_tiles_overlay.add(target.pos)
#                self.targetting_mode_sprites_under_click.add(sp)
            
    def set_effect_area_tiles(self, mappos):
        old_effect_area = self.effect_area_overlay
        if mappos:
            if hasattr(self.effect_area_func, '__call__') \
            and self.use_effect_area_func:  # to test if funcs are callable
                self.effect_area_overlay = self.effect_area_func(self.viewing_map_section, mappos, self.game)
            else:
                self.effect_area_overlay = set()
        else:
            self.effect_area_overlay = set()
        if old_effect_area != self.effect_area_overlay: 
            eV = UpdateMap()
            queue.put(eV)
        
    def set_effect_area_func(self, new_func = None):
        if hasattr(new_func, '__call__'):  # to test if funcs are callable
            self.effect_area_func = new_func
            self.use_effect_area_func = True
        else:
            self.effect_area_func = None
            self.use_effect_area_func = False
            
    def test_effect_area_func(self, mappos):
        x = mappos[0]
        y = mappos[1]
        effect_area = set()
        effect_area.add((x-1,y))
        effect_area.add((x-1,y-1))
        effect_area.add((x,y-1))
        effect_area.add((x+1,y-1))
        effect_area.add((x+1,y))
        effect_area.add((x+1,y+1))
        effect_area.add((x,y+1))
        effect_area.add((x-1,y+1))
        return effect_area

    def updateMap(self,doallviewedtiles = True, doRefresh = True):
        #Update everything on the whole viewable surface, not drawn to screen though
        #self.myUnitSprites.clear( self.gameMap, self.gameTerrain )


        #self.otherteamVisUnitSprites.clear( self.viewableMap, self.dimTerrain )
        #self.myUnitSprites.clear( self.viewableMap, self.dimTerrain )
        #self.viewCircleSprites.clear( self.viewableMap, self.dimTerrain )
        #self.visOrderSprites.clear( self.viewableMap, self.dimTerrain )
        print 'mainview', 'update map'
        zl = self.zoomlevel
        if self.selectedSprite:
            obj = self.selectedSprite.object
            if not self.target_mode:
                self.set_allowed_move_tiles(obj.allowed_move_tiles)
            else:
                self.set_allowed_target_tiles_and_objects(obj.allowed_target_locs, obj.allowed_targets) 
        else:
            self.set_allowed_move_tiles(set())
            self.set_allowed_target_tiles_and_objects(set(), set()) 
                
        self.putViewedTiles(doallviewedtiles)
        
        self.allMapSprites.empty()
        
        for sp in self.party_sprites:
            self.allMapSprites.add(sp)
            
            if self.showallunitorders or sp == self.selectedSprite:
                for ol_sp in sp.order_lines:
                    self.allMapSprites.add(ol_sp)

        if SHARED_SIGHT:
            for sp in self.party_sprites:
                advchar = sp.object
                for obj_id in advchar.visible_otherteam_ids:
                    obj = self.game.objectIdDict[obj_id]
                    obj_sp = self.uv.show_sprite_of_object(obj, updatemap = False, group = self.monster_sprites)
                    self.allMapSprites.add(obj_sp)
                for obj_id in advchar.visible_object_ids:
                    obj = self.game.objectIdDict[obj_id]
                    obj_sp = self.uv.show_sprite_of_object(obj, updatemap = False, group = self.object_sprites)
                    self.allMapSprites.add(obj_sp)
        else:
            if self.selectedSprite:
                if self.selectedSprite.type == 'playerchar':
                    advchar = self.selectedSprite.object
                    for obj_id in advchar.visible_otherteam_ids:
                        obj = self.game.objectIdDict[obj_id]
                        sp = self.uv.show_sprite_of_object(obj, updatemap = False, group = self.monster_sprites)
                        self.allMapSprites.add(sp)
                    for obj_id in advchar.visible_object_ids:
                        obj = self.game.objectIdDict[obj_id]
                        sp = self.uv.show_sprite_of_object(obj, updatemap = False, group = self.object_sprites)
                        self.allMapSprites.add(sp)
        
        
        #self.putViewedTiles(True)
#        self.viewableMap[zl].blit(self.viewedTerrain[zl], (0,0) )
        
#        self.allMapSprites.draw(self.viewableMap[zl])

#           self.myUnitSprites.draw( self.gameMap )
        '''self.viewCircleSprites.draw( self.viewableMap[zl] )
        self.citySprites.draw( self.viewableMap[zl] )
        self.otherteamVisUnitSprites.draw( self.viewableMap[zl] )

        self.teamUnitSprites.draw( self.viewableMap[zl] )
        
        self.orderLineSprites.draw( self.viewableMap[zl] )

        #for i in self.OrderLines:
            #pygame.draw.line(self.viewableMap[zl], i[0], i[1], i[2], 4)

        self.visOrderSprites.draw( self.viewableMap[zl] )

        self.myUnitSprites.draw( self.viewableMap[zl] )'''


##          if self.selectedObj:
##              if hasattr(self.selectedObj, "unit"):
##                  self.selectionSprite.rect.center = self.selectedObj.unit.pos
##                  self.gameMap.blit(self.selectionSprite.image,self.selectionSprite.rect)

        #self.updateSelectionWindow()

        self.old_map_pos_hover = None
        self.UpdateMiniMap()
        if doRefresh:
            self.view_refresh_needed = True
            print 'mainview, vrn5'

    def updateViewEvent(self):

        '''
        mapRect is a rect the size of the map view port.  It identifies a rectangle on the 
        viewable surface that should show up on screen.
        
        viewable surface is what I call the entire map plus any black border.  There is
        a viewable surface for each zoomlevel.  These surfaces aren't actually created
        (any more), but the concept is still used.  
        
        viewedTerrain, dimTerrain, and brightTerrain are actual surfaces of size 
        mapdim x tilepixsize.  For example if a map is 100x100 positions and the 
        tilepixsize is 8, then these surfaces are 800x800 pixels.  There is no black
        border on these surfaces.
        
        preZoomedRect is a rectangle that is applied to viewedTerrain and represents the
        portion of viewedTerrain that will be shown on the screen.  The size of 
        preZoomedRect is different for each zoom level.
        
        backSurf is the same size as map view port.  It is the surface that is ultimately
        blitted to the window (the display).  Black border might be present on this.
        
        MapTL is the top left location in the window (= the display = backSurf) at which 
        actual map (as opposed to black border) is shown.  Often this will be (0,0),
        but if one is zoomed out (and thus black border is present), then this won't 
        equal (0,0).
        
        For example, consider a map that is 100x100 positions.  Let a tile pixel size of 8 
        be zoomfactor 1.0. If the map view port were 1000 wide and 600 tall, the mapRect 
        would be 1000x600, and the viewable surface would be 1000x800. There would be a 
        black border of 100 on the left and right.  If the top left of mapRect were (0,0),
        then the screen would show pixels (0,0) to (999,599), or map locations (0,0) to 
        (99,74).  If the top left of mapRect were (0,64), then the screen would show
        pixels from (0,64) to (999,663), or map locations from (0,8) to (99,82).  The left
        coordinate of mapRect would always have to be 0 at this zoomfactor.  
        At a zoomfactor of 2.0, the viewable surface would be 1600x1600 pixels and there
        would be no black borders.  If the top left of mapRect were (0,0), then the screen
        would show pixels (0,0) to (999,599), or map locations from (0,0) to (61.5,36.5).   
        '''

        if not self.view_refresh_needed \
        and ((len(self.pguapp.widget.toupdate) == 1 and isinstance(self.pguapp.widget.toupdate.keys()[0], toppanel.TopPanel)) \
        or (len(self.pguapp.widget.topaint) == 1 and isinstance(self.pguapp.widget.topaint.keys()[0], toppanel.TopPanel))):
#            self.pguapp.refresh(forcePaint = True)
            self.pguctrl.tp.update(self.pguapp.screen)
            self.pguctrl.tp.paint(self.pguapp.screen)
            pygame.display.update()
        
        elif self.view_refresh_needed or self.pguapp.widget.toupdate or self.pguapp.widget.topaint:
#        if self.view_refresh_needed or self.pguapp.widget.toupdate or self.pguapp.widget.topaint:
#            print 'mainview, updateview', self.view_refresh_needed, self.pguapp.widget.toupdate, self.pguapp.widget.topaint
#            if self.movierunning and self.movie.frame == 7:
#                pass 
#        if self.view_refresh_needed:

            self.backSurf.fill( (0,0,0) )
#            pzr = self.preZoomedRect[self.zoomlevel]
            surf1 = self.viewedTerrain.subsurface(self.preZoomedRect[self.zoomlevel])
#            pygame.transform.scale(surf1, self.mapOSDim[self.zoomlevel], self.backSurf)

#            surf1 = surf1.copy()
#            pzrl = self.preZoomedRect[self.zoomlevel].left
#            pzrt = self.preZoomedRect[self.zoomlevel].top  
#            for sp in self.allMapSprites:
#                print 'mainview, updateview', self.zoomlevel, pzrl, pzrt, sp.rect.topleft          
#                if sp.rect.colliderect(self.preZoomedRect[self.zoomlevel]):
#                    surf1.blit(sp.image, (sp.rect.left-pzrl, sp.rect.top - pzrt) )
            
            tempsurf = pygame.transform.scale(surf1, self.mapOSDim[self.zoomlevel])
            self.backSurf.blit(tempsurf, self.MapTL[self.zoomlevel])

            mrl = self.mapRect.left
            mrt = self.mapRect.top  
            print 'mainview, updateview', self.zoomlevel, mrl, mrt, self.preZoomedRect[self.zoomlevel].topleft          
            for sp in self.allMapSprites:
                if sp.rect.colliderect(self.mapRect):
                    self.backSurf.blit(sp.image, (sp.rect.left-mrl, sp.rect.top - mrt) )
                    
            self.window.blit(self.backSurf, self.mapViewPortRect.topleft)

            #self.window.blit(self.gameMap,(0,0),self.mapRect)
#            self.window.blit(self.viewableMap[self.zoomlevel],self.mapViewPortRect.topleft,self.mapRect)
            self.window.blit(self.miniMapAll, self.minimaprect.topleft)
            # take unitwindow and brwindow out of this event?  update them separately?
            #self.window.blit(self.toppanelWindow, self.toppanelrect.topleft)
            #self.window.blit(self.infoWindow, self.infowindowrect.topleft)
            self.window.blit(self.selectionWindow, self.selectionwinrect.topleft)
            
            #self.app.paint(self.window)
            self.pguapp.refresh(forcePaint = True)
            
            self.refreshiw = True
            
            pygame.display.update()
            self.view_refresh_needed = False
            
#        pygame.display.update()

            

    #----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, UpdateViewEvent ):

            self.updateViewEvent()

        elif isinstance( event, UpdateMap ):

            self.updateMap(event.doallviewedtiles, event.doRefresh)

        elif isinstance( event, MouseoverEvent ):
            
            self.mouseOver(event.mousepos)


        elif isinstance (event, MapMoveRequest):
            self.RequestMapMove(event.topleftreq)

        elif isinstance (event, ScrollMapRequest):
            if not self.mapscrollLocked:
                if event.scrolldir == DIRECTION_UP:
                    newtopleftreq = (self.mapRect.left, self.mapRect.top - scroll_jump)
                elif event.scrolldir == DIRECTION_DOWN:
                    newtopleftreq = (self.mapRect.left, self.mapRect.top + scroll_jump)
                elif event.scrolldir == DIRECTION_LEFT:
                    newtopleftreq = (self.mapRect.left - scroll_jump, self.mapRect.top)
                elif event.scrolldir == DIRECTION_RIGHT:
                    newtopleftreq = (self.mapRect.left+ scroll_jump, self.mapRect.top)

            #eV = MapMoveRequest(newtopleftreq)
            #queue.put(eV)
                self.RequestMapMove(newtopleftreq)

        elif isinstance (event, ToggleShowAllUnitOrders):

            if self.showallunitorders == 1:
                self.showallunitorders = 0
            else:
                self.showallunitorders = 1

            eV = ShowOrders()
            queue.put(eV)

        elif isinstance( event, MapBuiltEvent ):
            self.setup_map(event.map)
            
        elif isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, LoadGraphicsEvent ):
            self.spriteVisuals = spritevisuals.SpriteVisuals(self.game, self)
            self.uv.transfer_SV_ref(self.spriteVisuals)

        elif isinstance( event, MapZoomRequest ):
            self.changeZoomReq(event)

        elif isinstance( event, MapZoomEvent ):
            self.changeZoom(event.pos)
            
        elif isinstance( event, MapLeftClickEvent ):
            self.mapLeftClickEvent(event.pos, event.shiftkeypressed)
            
        elif isinstance( event, MapRightClickEvent ):
            self.mapRightClickEvent(event.pos, event.keymods, event.target_mode)
            
        elif isinstance( event, SelectionWindowLeftClickEvent ):
            self.selectionWindowLeftClickEvent(event.pos, event.mods, event.pursuemode)

        elif isinstance( event, SelectionWindowRightClickEvent ):
            self.selectionWindowRightClickEvent(event.pos, event.mods, event.pursuemode)

        elif isinstance( event, ClearSelectionWindow ):
            self.selectionWindowSpritesUpper.empty()
            self.updateSelectionWindow()
            
        elif isinstance( event, ShowMovie ):
            self.movierunning = True
            self.movie.Start(event.visevents)

#        elif isinstance( event, PassUnitViewRef ):
#            self.uv = event.uvref
            
        elif isinstance( event, SelectRectEvent ):
            self.drawSelectRect(event.pos1, event.pos2)

        elif isinstance( event, MiniMapRightClickEvent ):
            self.miniMapRightClickEvent(event.pos, event.pursuemode)
            
        elif isinstance( event, SetAllowedMovesVisualsEvent ):
            pass
#            self.set_allowed_moves(event.object)

        elif isinstance( event, MakeTilesKnownEvent ):
            self.make_tiles_known(event.newly_known_tiles)

        elif isinstance( event, ShowDefaultInfoPopupEvent ):
            self.show_default_info_popup(event.msg)

        elif isinstance( event, ShowDefaultChoicePopup ):
            self.show_default_choice_popup(event.data, event.choice_func)

        elif isinstance( event, ShowTimedMessageEvent ):
            surf = self.show_timed_msg(event.msg, event.add_to_list)
