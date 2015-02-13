

import pygame
from pygame.locals import *

#from events import *
#from evmanager import *
#from game import *
#from gamefunctions import *
#from mainview import *
from userconstants import *
from fontdefs import *
import yaml
import random





class UnitSprite(pygame.sprite.Sprite):
    def __init__(self, group = None ):
        pygame.sprite.Sprite.__init__(self, group)

#------------------------------------------------------------------------------
class MakeBasicSprites(pygame.sprite.Sprite):
    def __init__(self, n, u ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (32,32) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,32)) #make transparent
        

        if u == 'Infantry':
            pygame.draw.rect( unitSurf0, color, (6,6,20,20) )
            pygame.draw.line( unitSurf0, (255,255,255,0), (6,6), (25,25), 2)
            pygame.draw.line( unitSurf0, (255,255,255,0), (25,6), (6,25), 2)
            #pygame.draw.rect( unitSurf0, color, (1,1,30,30) )
            #pygame.draw.line( unitSurf0, (255,255,255), (1,1), (30,30), 2)
            #pygame.draw.line( unitSurf0, (255,255,255), (30,1), (1,30), 2)
        elif u == 'Armor':
            pygame.draw.rect( unitSurf0, color, (1,1,30,30) )
            pygame.draw.ellipse( unitSurf0, (255,255,255), (1,6,29,19), 2 )

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeBasicMedSprites(pygame.sprite.Sprite):
    def __init__(self, n, u ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (16,16) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        if u == 'Infantry':
            pygame.draw.rect( unitSurf0, color, (1,1,14,14) )
            pygame.draw.line( unitSurf0, (255,255,255,255), (1,1), (14,14), 2)
            pygame.draw.line( unitSurf0, (255,255,255,255), (14,1), (1,14), 2)
        elif u == 'Armor':
            pygame.draw.rect( unitSurf0, color, (1,1,14,14) )
            pygame.draw.ellipse( unitSurf0, (255,255,255,255), (1,4,15,9), 2 )

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeBasicMiniSprites(pygame.sprite.Sprite):
    def __init__(self, n, u ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (4,4) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        if u == 'Infantry':
            pygame.draw.rect( unitSurf0, color, (0,0,4,4) )
            #pygame.draw.line( unitSurf0, (255,255,255), (1,1), (14,14), 2)
            #pygame.draw.line( unitSurf0, (255,255,255), (14,1), (1,14), 2)
        elif u == 'Armor':
            pygame.draw.rect( unitSurf0, color, (0,0,4,4) )
            #pygame.draw.ellipse( unitSurf0, (255,255,255), (1,4,14,7), 2 )

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeUnitGroupSprites(pygame.sprite.Sprite):
    def __init__(self, n, CapChar, font ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (32,32) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        pygame.draw.rect( unitSurf0, color, (1,1,30,30) )
        fontsurf = font.render(CapChar, 1, (255,255,255), color)
        unitSurf0.blit(fontsurf,(3,1))

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeMedUnitGroupSprites(pygame.sprite.Sprite):
    def __init__(self, n, CapChar, font ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (16,16) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        pygame.draw.rect( unitSurf0, color, (1,1,14,14) )
        fontsurf = font.render(CapChar, 1, (255,255,255), color)
        unitSurf0.blit(fontsurf,(2,1))

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeMiniUnitGroupSprites(pygame.sprite.Sprite):
    def __init__(self, n ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (4,4) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        pygame.draw.rect( unitSurf0, color, (0,0,4,4) )
        #fontsurf = font.render(CapChar, 1, (255,255,255), color)
        #unitSurf0.blit(fontsurf,(2,1))

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0

class MakeCitySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (32,32) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0))

        pygame.draw.circle( unitSurf, color, (16,16), 10)
        pygame.draw.circle( unitSurf, (1,1,1), (16,16), 12, 3)
        pygame.draw.circle( unitSurf, (253,253,253), (16,16), 14, 3)
        pygame.draw.circle( unitSurf, (1,1,1), (16,16), 16, 2)

        self.rect  = unitSurf.get_rect()
        self.image = unitSurf

class MakeMedCitySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (16,16) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0))

        pygame.draw.circle( unitSurf, color, (8,8), 5)
        pygame.draw.circle( unitSurf, (1,1,1), (8,8), 6, 1)
        pygame.draw.circle( unitSurf, (253,253,253), (8,8), 7, 1)
        pygame.draw.circle( unitSurf, (1,1,1), (8,8), 8, 1)

        self.rect  = unitSurf.get_rect()
        self.image = unitSurf

class MakeMiniCitySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (5,5) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,1,0))

        pygame.draw.circle( unitSurf, color, (2,2), 2)
        pygame.draw.circle( unitSurf, (253,253,253), (2,2), 2, 1)
        #pygame.draw.circle( unitSurf, (253,253,253), (16,16), 14, 3)
        #pygame.draw.circle( unitSurf, (1,1,1), (16,16), 16, 2)

        self.rect  = unitSurf.get_rect()
        self.image = unitSurf

class MakeSupplySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (6,12) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent
        
        pygame.draw.rect( unitSurf0, color, (0,0,6,12))

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0
        
class CreateRotatedSupplyImage(pygame.Surface):
    def __init__(self, surf, angle):
        
        pygame.Surface.__init__( self, (32,32), pygame.SRCALPHA )
        newsurf = pygame.transform.rotate(surf, angle)
        newrect = newsurf.get_rect()
        selfrect = self.get_rect()
        newrect.center = selfrect.center 
        self.blit(newsurf, newrect.topleft) 

class MakeMedSupplySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (16,16) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0))

        pygame.draw.rect( unitSurf, color, (5,2,6,12))

        self.rect  = unitSurf.get_rect()
        self.image = unitSurf

class MakeMiniSupplySprite (pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (4,4) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0))

        pygame.draw.rect( unitSurf, color, (0,0,4,4))

        self.rect  = unitSurf.get_rect()
        self.image = unitSurf


class OrderSprite(pygame.sprite.Sprite):
    def __init__(self, otype, ocolor, font, textcolor ):
        pygame.sprite.Sprite.__init__(self)

        color = ocolor
        
#        if ocolor == 'green':
#            color = (0,240,0)
#        elif ocolor == 'yellow':
#            color = (240, 240, 0)
#        elif ocolor == 'red':
#            color = (240, 0, 0)

        colortag = font.render('M', 0, textcolor, color)
        colortagrect = colortag.get_rect(center = (12,12))

        unitSurf = pygame.Surface( (24,24) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0)) #make transparent

        if otype == 'move':
            pygame.draw.circle( unitSurf, color, (12,12), 11)
        elif otype == 'status':
            pygame.draw.rect( unitSurf, color, (1,1,22,22))

        unitSurf.blit( colortag, colortagrect )

        self.image = unitSurf
        self.rect = unitSurf.get_rect()

class TurnSprite(pygame.sprite.Sprite):
    def __init__(self, otype, ocolor, onum, font, textcolor ):
        pygame.sprite.Sprite.__init__(self)
        
        color = ocolor

#        if ocolor == 'green':
#            color = (0,240,0)
#        elif ocolor == 'yellow':
#            color = (240, 240, 0)
#        elif ocolor == 'red':
#            color = (240, 0, 0)

        colortag = font.render(str(onum), 0, textcolor, color)
        colortagrect = colortag.get_rect(center = (12,12))

        unitSurf = pygame.Surface( (24,24) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,0,0,0)) #make transparent

        if otype == 'turn':
            pygame.draw.circle( unitSurf, color, (12,12), 11)
#        elif otype == 'status':
#            pygame.draw.rect( unitSurf, color, (1,1,22,22))

        unitSurf.blit( colortag, colortagrect )

        self.image = unitSurf
        self.rect = unitSurf.get_rect()


class AllowedMoveSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
#        colortag = font.render(str(onum), 0, textcolor, color)
#        colortagrect = colortag.get_rect(center = (12,12))

        unitSurf = pygame.Surface( (tilepixsize,tilepixsize) )
        unitSurf = unitSurf.convert_alpha()
        unitSurf.fill((0,240,0,25)) #make transparent

        self.image = unitSurf
        self.rect = unitSurf.get_rect()


class SelectionSprite(pygame.sprite.Sprite):
    def __init__( self ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (tilepixsize,tilepixsize) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        self.rect  = unitSurf0.get_rect()
        pygame.draw.rect( unitSurf0, (255,255,255), self.rect, 1)   # the selected sprite

        self.image = unitSurf0

class PursuedSelectionSprite(pygame.sprite.Sprite):
    def __init__( self ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (tilepixsize,tilepixsize) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        self.rect  = unitSurf0.get_rect()
        pygame.draw.rect( unitSurf0, (255,255,0), self.rect, 2)   # the selected sprite

        self.image = unitSurf0

class medSelectionSprite(pygame.sprite.Sprite):
    def __init__( self ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (16,16) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        self.rect  = unitSurf0.get_rect()
        pygame.draw.rect( unitSurf0, (255,255,255), self.rect, 2)   # the selected sprite

        self.image = unitSurf0

class PursuedmedSelectionSprite(pygame.sprite.Sprite):
    def __init__( self ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf0 = pygame.Surface( (16,16) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,0)) #make transparent

        self.rect  = unitSurf0.get_rect()
        pygame.draw.rect( unitSurf0, (255,255,0), self.rect, 2)   # the selected sprite

        self.image = unitSurf0

class ViewMaskSprite(pygame.sprite.Sprite):
    # The general method is: a square of the proper size is grabbed from gameTerrain (bright)
    # Then a square with a transparent circle in the middle (and opague "corners") is blitted
    # on to the grabbed square.  The corners are then set to be transparent, and
    # the new square is blitted on to dimTerrain.

    def __init__( self, radius ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (radius*2,radius*2) )
        #unitSurf = unitSurf.convert_alpha()

        #unitSurf.fill((0,0,0,0)) #make transparent
        unitSurf.fill((0,1,0))

        self.rect  = unitSurf.get_rect()
        pygame.draw.circle( unitSurf, (255,254,255), (radius,radius), radius)

        unitSurf.set_colorkey((255,254,255))

        self.image = unitSurf


class minimapViewMaskSprite(pygame.sprite.Sprite):
    # Will be squished (elliptical) if main map doesn't have same aspect ratio as minimap

    def __init__( self, xdim, ydim ):
        pygame.sprite.Sprite.__init__(self)

        unitSurf = pygame.Surface( (xdim*2, ydim*2) )
        #unitSurf = unitSurf.convert_alpha()

        #unitSurf.fill((0,0,0,0)) #make transparent
        unitSurf.fill((0,1,0))

        self.rect  = unitSurf.get_rect()
        pygame.draw.ellipse( unitSurf, (255,254,255), self.rect)

        unitSurf.set_colorkey((255,254,255))

        self.image = unitSurf


class MakeBasicSprites(pygame.sprite.Sprite):
    def __init__(self, n, u ):
        pygame.sprite.Sprite.__init__(self)

        color = n.color

        unitSurf0 = pygame.Surface( (32,32) )
        unitSurf0 = unitSurf0.convert_alpha()
        unitSurf0.fill((0,0,0,32)) #make transparent
        

        if u == 'Infantry':
            pygame.draw.rect( unitSurf0, color, (6,6,20,20) )
            pygame.draw.line( unitSurf0, (255,255,255,0), (6,6), (25,25), 2)
            pygame.draw.line( unitSurf0, (255,255,255,0), (25,6), (6,25), 2)
            #pygame.draw.rect( unitSurf0, color, (1,1,30,30) )
            #pygame.draw.line( unitSurf0, (255,255,255), (1,1), (30,30), 2)
            #pygame.draw.line( unitSurf0, (255,255,255), (30,1), (1,30), 2)
        elif u == 'Armor':
            pygame.draw.rect( unitSurf0, color, (1,1,30,30) )
            pygame.draw.ellipse( unitSurf0, (255,255,255), (1,6,29,19), 2 )

        self.rect  = unitSurf0.get_rect()
        self.image = unitSurf0


class SpriteVisuals:
    def __init__(self, game, view):

        self.turnSpriteDict = {}

        self.player_tile_dict = {}
        thispath = os.path.join(resourcepath,'player.gfx')
        f = open(thispath, 'r')
        pgfx_prefs = yaml.load(f)
        f.close()
        
        temp_dict = {}
        
        for ptype,stypedict in pgfx_prefs.iteritems():
            for stype,varianttilelist in stypedict.iteritems():
                tsurf2 = []
                for varianttile in varianttilelist:
                    pathtilefn = os.path.join(playertilespath,varianttile)
                    tsurf = pygame.image.load(pathtilefn)
                    tsurf = tsurf.convert_alpha()
                    
                    tsurf2.append(tsurf)
                temp_dict[(ptype,stype)] = tsurf2

        for pcharid in game.charnamesid.values():
            pchar = game.objectIdDict[pcharid]
            self.player_tile_dict[pchar.name] = random.choice(temp_dict[(pchar.race,pchar.advclasses.keys()[0])])
                # todo, this needs to be the same each time same game loads


        self.monster_tile_dict = {}
        thispath = os.path.join(resourcepath,'monster.gfx')
        f = open(thispath, 'r')
        mgfx_prefs = yaml.load(f)
        f.close()
        
        for species,varianttilelist in mgfx_prefs.iteritems():
#            for stype,varianttilelist in stypedict.iteritems():
            tsurf2 = []
            for varianttile in varianttilelist:
                pathtilefn = os.path.join(monstertilespath,varianttile)
                tsurf = pygame.image.load(pathtilefn)
                tsurf = tsurf.convert_alpha()
                
                tsurf2.append(tsurf)
            self.monster_tile_dict[species] = tsurf2
#        for ptype,stypedict in mgfx_prefs.iteritems():
#            for stype,varianttilelist in stypedict.iteritems():
#                tsurf2 = []
#                for varianttile in varianttilelist:
#                    pathtilefn = os.path.join(monstertilespath,varianttile)
#                    tsurf = pygame.image.load(pathtilefn)
#                    tsurf = tsurf.convert_alpha()
#                    
#                    tsurf2.append(tsurf)
#                self.monster_tile_dict[(ptype,stype)] = tsurf2
        # todo, create a default sprite for when no graphic has been defined


        self.object_tile_dict = {}
        thispath = os.path.join(resourcepath,'object.gfx')
        f = open(thispath, 'r')
        ogfx_prefs = yaml.load(f)
        f.close()
        for k,v in ogfx_prefs.iteritems():
            if type(v) is dict:
                ptype = k
                for stype,varianttilelist in v.iteritems():
                    tsurf2 = []
                    for varianttile in varianttilelist:
                        pathtilefn = os.path.join(objecttilespath,varianttile)
                        tsurf = pygame.image.load(pathtilefn)
                        tsurf = tsurf.convert_alpha()
                        tsurf2.append(tsurf)
                    self.object_tile_dict[(ptype,stype)] = tsurf2
            else:
                tsurf2 = []
                for varianttile in v:
                    pathtilefn = os.path.join(objecttilespath,varianttile)
                    tsurf = pygame.image.load(pathtilefn)
                    tsurf = tsurf.convert_alpha()
                    tsurf2.append(tsurf)
                self.object_tile_dict[k] = tsurf2
        # todo, create a default sprite for when no graphic has been defined



        numordercolors = len(userconst_ordercolors)
        self.ordercolors = []
        for i in range(maxturnsorders):
            for idx,oc in enumerate(userconst_ordercolors):
                textcolor = userconst_ordertextcolor[idx]
                self.turnSpriteDict[oc, i+1] = TurnSprite('turn', oc, i+1, fontdefault20,textcolor)

            if i >= numordercolors:
                self.ordercolors.append(userconst_ordercolors[-1])
            else:
                self.ordercolors.append(userconst_ordercolors[i])
                
        self.allowed_move_sprite = AllowedMoveSprite()


def createLineSprite(color, vsstartpos, vsendpos):
    
    surfwidth = abs(vsstartpos[0]-vsendpos[0])+4
    surfheight = abs(vsstartpos[1]-vsendpos[1])+4
    left = min( (vsstartpos[0],vsendpos[0]) )
    top = min( (vsstartpos[1],vsendpos[1]) )
    rectstart = ( vsstartpos[0] - left, vsstartpos[1] - top )
    rectend = ( vsendpos[0] - left, vsendpos[1] - top )
    
    rectSurf = pygame.Surface( ( surfwidth,surfheight ) )
    rectSurf.fill( (0,1,0) )
    pygame.draw.line(rectSurf, color, rectstart, rectend, 4)
    
    rectSurf.set_colorkey((0,1,0))

    newSprite = pygame.sprite.Sprite()

    newSprite.rect  = rectSurf.get_rect()
    newSprite.image = rectSurf
    newSprite.rect.topleft = (left,top)     
    
    return newSprite

def calcLineSeg(view, startpos, endpos):
    vsstartpos = view.convertMapPosToViewSurfPos(startpos)
    vsendpos = view.convertMapPosToViewSurfPos(endpos)
    
    splitlinex = False
    splitliney = False
    vse1x = None
    vse1y = None
    vss2x = None
    vss2y = None
    
    if wrap_East_West:
        if startpos[0] - endpos[0] > 1:
            splitlinex = True
            vse1x = view.convertMapPosToTLViewSurfPos((startpos[0]+1,startpos[1]))[0] - 1
                                                                # gives right edge
                                                                # of start tile
            vss2x = view.convertMapPosToTLViewSurfPos(endpos)[0]     # gives left edge
                                                                # of end tile
            
        elif endpos[0] - startpos[0] > 1:
            splitlinex = True
            vse1x = view.convertMapPosToTLViewSurfPos(startpos)[0]   # gives left edge
                                                                # of start tile
            vss2x = view.convertMapPosToTLViewSurfPos((endpos[0]+1,endpos[1]))[0] - 1
                                                                # gives right edge
                                                                # of end tile

    if wrap_North_South:
        if startpos[1] - endpos[1] > 1:
            splitliney = True
            vse1y = view.convertMapPosToTLViewSurfPos((startpos[0],startpos[1]+1))[1] - 1
                                                                # gives bottom edge
                                                                # of start tile
            vss2y = view.convertMapPosToTLViewSurfPos(endpos)[1]     # gives top edge
                                                                # of end tile
            
        elif endpos[1] - startpos[1] > 1:
            splitliney = True
            vse1y = view.convertMapPosToTLViewSurfPos(startpos)[1]   # gives top edge
                                                                # of start tile
            vss2y = view.convertMapPosToTLViewSurfPos((endpos[0],endpos[1]+1))[1] - 1
                                                                # gives bottom edge
                                                                # of end tile
        
    if splitlinex and not splitliney:
        vse1y = (vsstartpos[1] + vsendpos[1]) / 2
        vss2y = vse1y
    elif splitliney and not splitlinex:
        vse1x = (vsstartpos[0] + vsendpos[0]) / 2
        vss2x = vse1x
        
    return vsstartpos, vsendpos, (vse1x,vse1y), (vss2x,vss2y), splitlinex, splitliney

def drawLineSeg(view, startpos, endpos, color, layer):
            
    vsstartpos, vsendpos, es1pos, ss2pos, splitlinex, splitliney = calcLineSeg(view, startpos, endpos)        
            
    new_sprites = []
    if splitlinex or splitliney:
        newSprite = createLineSprite(color, vsstartpos, es1pos)
        newSprite._layer = layer
        new_sprites.append(newSprite)
#        view.order_lines.append(newSprite)   
#        view.allMapSprites.add(newSprite)
        
        newSprite = createLineSprite(color, ss2pos, vsendpos)
        newSprite._layer = layer   
        new_sprites.append(newSprite)
#        view.order_lines.append(newSprite)   
#        view.allMapSprites.add(newSprite)
        
    else:
        newSprite = createLineSprite(color, vsstartpos, vsendpos)
        newSprite._layer = layer   
        new_sprites.append(newSprite)
#        view.order_lines.append(newSprite)   
#        view.allMapSprites.add(newSprite)

    return new_sprites
    
def createRectSprite(color, vsstartpos, vsendpos):
    
    surfwidth = abs(vsstartpos[0]-vsendpos[0])
    surfheight = abs(vsstartpos[1]-vsendpos[1])
    left = min( (vsstartpos[0],vsendpos[0]) )
    top = min( (vsstartpos[1],vsendpos[1]) )
    
    unitSurf0 = pygame.Surface( ( surfwidth,surfheight ) )
    unitSurf0 = unitSurf0.convert_alpha()
    unitSurf0.fill((0,0,0,0)) #make transparent

    usrect  = unitSurf0.get_rect()
    pygame.draw.rect( unitSurf0, color, usrect, 1)   # the selected sprite

#    self.image = unitSurf0
#
#    
#    
#    rectstart = ( vsstartpos[0] - left, vsstartpos[1] - top )
#    rectend = ( vsendpos[0] - left, vsendpos[1] - top )
#    
#    rectSurf = pygame.Surface( ( surfwidth,surfheight ) )
#    rectSurf.fill( (0,1,0) )
#    pygame.draw.line(rectSurf, color, rectstart, rectend, 4)
#    
#    rectSurf.set_colorkey((0,1,0))
    newSprite = pygame.sprite.Sprite()

    newSprite.image = unitSurf0
    newSprite.rect  = usrect
    newSprite.rect.topleft = (left,top)     
    
    return newSprite


