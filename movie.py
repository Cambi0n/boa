import Queue
import pygame
from pygame.locals import *
from gamefunctions import *
#from game import *
#from game import Unit
from clientroundresults import *
from userconstants import *

from events import *
from evmanager import *
import view_utils


class Movie():
    def __init__(self, evManager, view, soundview):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        
        self.view = view
        
        self.soundView = soundview
        self.frame = 0
        
        self.deleted_object_ids = []

    def showMovieFrame(self,movedir = 1, updateMap = True):

        #self.ResetToTurnBeginning(uv)

        self.frame = self.frame + movedir
        np = self.frame
        
#        if self.frame >= self.numframes:
            

#        if self.validframesleft:
        print 'showmovieframe', np
        if movedir == 1:
            if self.frame >= self.endatframe:
                pygame.time.set_timer(SHOW_MOVIEFRAME, 0)
                self.uv.view.movierunning = False
            if self.frame > self.endatframe:
                self.frame = self.endatframe
                return
            else:
                ordlist = self.visevents[np-1]
        else:
            if self.frame <= self.endatframe:
                pygame.time.set_timer(SHOW_MOVIEFRAME, 0)
                self.uv.view.movierunning = False
            if self.frame < self.endatframe:
                self.frame = self.endatframe
                return
            else:
#                print self.visevents
                ordlist = self.visevents[np]
        numorders_thispulse = len(ordlist)
        if movedir == 1:
            ordnumlist = range(numorders_thispulse)
        else:
            ordnumlist = range(numorders_thispulse-1,-1,-1)
            
        needToUpdateOrderView = False
        need_to_update_map = False
        
        for ordnum in ordnumlist:
            thisorder = ordlist[ordnum]
#        for ordnum in range(numorders_thispulse):
#            thisorder = ordlist[ordnum]
            uid = thisorder[0]
            ordtype = thisorder[1]
            
            print 'movie, showmovieframe', ordtype

            if ordtype == 'move':
                unit = self.game.objectIdDict[uid]
#                unit.setPosition(thisorder[2], self.game)
                print 'in movie, move', unit.orders, uid, unit
                if movedir == 1:
#                    if unit.nation == self.uv.game.mynation and unit.orders[0][0] != 'pursue target':
#                        unit.orders[0][1].pop(0)
                    unit.setPosition(thisorder[2])
                    unit.popPath(self.game)
                else:
#                    if unit.nation == self.uv.game.mynation and unit.orders[0][0] != 'pursue target':
#                        unit.orders[0][1].insert(0,thisorder[2])
                    unit.setPosition(thisorder[3])
                    unit.unPopPath(thisorder[2], self.game)
                objectSprite = self.uv.GetObjectSprite(unit,self.view.allMapSprites)
                if objectSprite:
                    self.uv.setSpriteLocation(objectSprite,unit.pos)
#                self.uv.show_sprite_of_object(unit,updatemap = False)
                needToUpdateOrderView = True
                need_to_update_map = True
                print 'in movie, move2', unit.orders, uid, unit
#                self.uv.showOrders()

            elif ordtype == 'pop0':
                unit = self.uv.game.objectIdDict[uid]
                print 'in movie, pop0', unit.orders, id(thisorder[2])
                if movedir == 1:
                    unit.pop_order(0)
                else:
                    unit.insert_order(deepcopy(thisorder[2]), 0)
#                    if unit.nation == self.uv.game.mynation:
#                        self.uv.showOrders()
                needToUpdateOrderView = True

            elif ordtype == 've_light_changes':
                light_changes = thisorder[2]
                map_section_name = thisorder[3]
                if movedir == 1:
                    view_utils.apply_tile_level_changes_to_total_levels(light_changes, self.game.map_data[map_section_name]['light'])
                else:
                    view_utils.remove_tile_level_changes_from_total_levels(light_changes, self.game.map_data[map_section_name]['light'])
                need_to_update_map = True    

            elif ordtype == 've_new_viewed_tiles':
                dict_of_view_info = thisorder[2]
                dict_of_view_changes = thisorder[3]
                if movedir == 1:
                    view_utils.apply_dict_of_view_set_changes_to_total_sets(dict_of_view_changes, self.game)
                    self.game.update_known_tiles(dict_of_view_changes)
                else:
                    view_utils.apply_dict_of_view_set_changes_to_total_sets(dict_of_view_changes, self.game, True)
                need_to_update_map = True    

            elif ordtype == 've_mover_vis_changes':
                mover_vis_changes = thisorder[2]
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    unit.apply_vis_changes(**mover_vis_changes)
                else:
                    unit.reverse_vis_changes(**mover_vis_changes)
                need_to_update_map = True    

            elif ordtype == 've_others_vis_changes_of_mobj':
                nonmover_vis_changes = thisorder[2]
                if movedir == 1:
                    view_utils.apply_others_vis_changes_of_mobj_id(uid, nonmover_vis_changes, self.game)
                else:
                    view_utils.reverse_others_vis_changes_of_mobj_id(uid, nonmover_vis_changes, self.game)
                need_to_update_map = True

            elif ordtype == 've_others_vis_changes_of_nonmobj':
                vis_changes = thisorder[2]
                if movedir == 1:
                    view_utils.apply_others_vis_changes_of_nonmobj_id(uid, vis_changes, self.game)
                else:
                    view_utils.reverse_others_vis_changes_of_nonmobj_id(uid, vis_changes, self.game)
                need_to_update_map = True

            elif ordtype == 've damage dealt':
                # todo - pop up a window or something about die rolls
                details = thisorder[2]
                enemyid = details['enemy_id']
                dam_tot_list = details['damage_total']
                dam_tot = 0
                for dam in dam_tot_list:
                    dam_tot += dam
                enemy_obj = self.game.objectIdDict[enemyid]
                if movedir == 1:
                    enemy_obj.change_damage(dam_tot)
                else:
                    enemy_obj.change_damage(-dam_tot)
                
            elif ordtype == 've assign exp':
                exp_dict = thisorder[2]
                if movedir == 1:
                    self.game.assign_exp_to_party_members(exp_dict)
                else:
                    self.game.assign_exp_to_party_members(exp_dict, reverse = True)
                    
                
            elif ordtype == 've lose vis of id':
                lostid = thisorder[2]
                ids_that_see = thisorder[3]
                print 'movie, ve lose vis of id', lostid, ids_that_see
                if movedir == 1:
                    view_utils.remove_id_from_other_vis_lists(lostid, ids_that_see, self.game)
                    for ida in ids_that_see:
                        obja = self.game.objectIdDict[ida]
                        print 'movie, ve lose vis of id2', obja.visible_otherteam_ids 
                else:
                    view_utils.add_id_to_other_vis_lists(lostid, ids_that_see, self.game)
                need_to_update_map = True    

            elif ordtype == 've dead':
                if uid not in self.deleted_object_ids:
                    self.deleted_object_ids.append(uid)
                    
            elif ordtype == 've set new orders':
                new_orders = thisorder[2]
                old_orders = thisorder[3]
                mobj = self.game.objectIdDict[uid]
                if movedir == 1:
                    mobj.set_new_orders(new_orders, self.game)
                else:
                    mobj.set_new_orders(old_orders, self.game)

            elif ordtype == 've append new order':
                new_orders = thisorder[2]
                mobj = self.game.objectIdDict[uid]
                if movedir == 1:
                    mobj.orders.append(new_orders)
                else:
                    mobj.orders.pop()

            elif ordtype == 've show message':
                if uid == 'game' or uid in self.game.charnamesid.itervalues():
                    self.view.show_timed_msg(thisorder[2])

            elif ordtype == 've drop item':
                mobj = self.game.objectIdDict[uid]
                item = self.game.objectIdDict[thisorder[2]]
                if movedir == 1:
                    mobj.drop_item(item, self.game)
                else:
                    mobj.pickup_item(item, self.game)

            elif ordtype == 've pickup item':
                mobj = self.game.objectIdDict[uid]
                item = self.game.objectIdDict[thisorder[2]]
                if movedir == 1:
                    mobj.pickup_item(item, self.game)
                else:
                    mobj.drop_item(item, self.game)


            elif ordtype == 've_update_energy':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    unit.set_current_energy(thisorder[2])
                else:
                    unit.set_current_energy(thisorder[3])
                    
            elif ordtype == 've_update_energy_ord':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    unit.set_current_energy_ord(thisorder[2])
                else:
                    unit.set_current_energy_ord(thisorder[3])
                    
            elif ordtype == 've_set_new_orders':
                print 'movie, set new orders', thisorder[2], thisorder[3], id(thisorder[2]), id(thisorder[3])
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    unit.set_new_orders(deepcopy(thisorder[2]), self.game)
                else:
                    unit.set_new_orders(deepcopy(thisorder[3]), self.game)
                    
            elif ordtype == 'vechangemode':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    self.game.unitActions.changeUnitMode(unit, thisorder[2], thisorder[3])
                else:
                    self.game.unitActions.changeUnitMode(unit, thisorder[2], thisorder[4])
                
                adjustViewLevels(unit, self.game)
                
            elif ordtype == 'veprogress':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    useord = 3
                else:
                    useord = 4
                    
                suborder = thisorder[2]
                if suborder == 'nextsq':
                     unit.setNextSqProg(thisorder[useord], self.game)
                elif suborder == 'load':
                     unit.setLoadProg(thisorder[useord], self.game)
                elif suborder == 'modechange':
                     unit.modechangeprogress = thisorder[useord]
                     
            elif ordtype == 'venewnextsq':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    useord = 2
                else:
                    useord = 3
                    
                unit.setNextSq(thisorder[useord], self.game)
                
            elif ordtype == 'pursue target':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    unit.orders.insert(0,['pursue target', thisorder[2]])
                else:
                    unit.orders.pop(0)
                    
            elif ordtype == 'sprite vanishes':
                unit = self.game.objectIdDict[uid]
                if movedir == 1:
                    if unit.team != self.game.myteam:
                        unit.visible_to.remove(self.game.myteam)
                    self.uv.hide_sprite_of_object(unit,False)
                else:
                    if unit.team != self.game.myteam:
                        unit.visible_to.append(self.game.myteam)
#                    self.uv.show_sprite_of_object(unit,updatemap = False)
                    
                print "in movie, sprite vanishes", uid, unit
                
            elif ordtype == 'sprite appears':
                
                udata = thisorder[2]
                pos = udata[0]
                if uid not in self.game.objectIdDict:
                    type = udata[1]
                    nationname = udata[2]
                    if type == "Supply":
                        eunit = units.SupplyUnit(nationname,type,pos,self.game,uid)
                    else:
                        eunit = units.Unit(nationname,type,pos,self.game,uid)
                else:
                    eunit = self.game.objectIdDict[uid]
                    eunit.pos = pos
                eunit.currenthitpoints = udata[3]
                if len(udata) >= 5:
                    eunit.orders = udata[4]
                
#                print 'in movie, sprite appears', eunit, eunit.id, eunit.visible_to, eunit.pos, eunit.orders
                if movedir == 1:
                    if eunit.team != self.game.myteam:
                        eunit.visible_to.append(self.game.myteam)
                        if self.playsounds:
                            ev = PlaySound(self.soundView.scarynote)
                            queue.put(ev)
#                    self.uv.show_sprite_of_object(eunit,updatemap = False)
                else:
                    if eunit.team != self.game.myteam:
                        eunit.visible_to.remove(self.game.myteam)
                    self.uv.hide_sprite_of_object(eunit,False)
                
            elif ordtype == 'damage taken':
                
                unit = self.game.objectIdDict[uid]
                udata = thisorder[2]
                if movedir == 1:
                    unit.currenthitpoints -= udata[0]   # udata[1] = attacking unit, will be
                                                        # used to provide feedback to defending unit
                    unation = udata[2]
                    if unation == self.game.mynation:
                        if self.playsounds:
                            ev = PlaySound(self.soundView.battle013)
                            queue.put(ev)
#                    print 'client turn results, damage taken', uid, unit.currenthitpoints, pulsenum
                else:
                    unit.currenthitpoints += udata[0]
                
            elif ordtype == 'damage observed':
                unit = self.game.objectIdDict[uid]
                udata = thisorder[2]
                if movedir == 1:
                    unit.currenthitpoints -= udata[0]   # udata[1] = attacking unit, will be
                                                        # used to provide feedback to defending unit
#                    unation = udata[2]
#                    if unation == self.uv.game.mynation:
#                        if self.playsounds:
#                            ev = PlaySound(self.soundView.battle013)
#                            queue.put(ev)
#                    print 'client turn results, damage observed', uid, unit.currenthitpoints, pulsenum
                else:
                    unit.currenthitpoints += udata[0]
                pass
                
            elif ordtype == 'damage dealt':
                pass    # will be used to provide feedback to attacker
                
            elif ordtype == 'unit deleted':
                if uid in self.game.objectIdDict:
                #udata = thisorder[2]
                #unation = udata[0]
                    unit = self.game.objectIdDict[uid]
                    groupdata = thisorder[2]
                    uNation = self.game.Nations[unit.nation]
                    if movedir == 1:
                        print 'movie delete unit', uid, unit.currenthitpoints
                        if groupdata[1] and uNation.team == self.game.myteam:
                            if groupdata[0]:    # was a 2 person group, now no group just 1 unit left
                                group = self.game.objectIdDict[groupdata[1]]
                                unitUG = self.game.objectIdDict[groupdata[0]]
                                ev = HandleGroupLeavingVisuals([unitUG],group,True, unit, False)
                                queue.put(ev)
                                #del self.game.objectIdDict[groupdata[1]]
                            else:       # group had more than 2 units, now one less
                                group = self.game.objectIdDict[groupdata[1]]
                                ev = HandleGroupLeavingVisuals([], group, False, unit, False)
                                queue.put(ev)
                        else:
                            self.uv.hide_sprite_of_object(unit,False)
                            
                        if unit.nation == self.game.mynation:
                            if self.playsounds:
                                ev = PlaySound(self.soundView.whistledown)
                                queue.put(ev)
                    else:
#                        self.uv.show_sprite_of_object(unit,updatemap = False)
                        if groupdata[1] and uNation.team == self.game.myteam:
                            if groupdata[0]:    # go back to a group
                                group = self.game.objectIdDict[groupdata[1]]
                                unitUG = self.game.objectIdDict[groupdata[0]]
                                ev = HandleGroupCreationVisuals(group,True,unit,True,unitUG,True, False)
                                queue.put(ev)
                            else:       # group had more than 2 units, now one more
                                group = self.game.objectIdDict[groupdata[1]]
                                ev = HandleGroupCreationVisuals(group, False, unit, True, group, False, False)
                                queue.put(ev)
 
            elif ordtype == 'veSupply Change':
               if uid in self.game.objectIdDict:
                   unit = self.game.objectIdDict[uid]
                   samts = thisorder[2]
                   supply.SupplyChange(samts, unit)
 
 
        if needToUpdateOrderView:
            self.uv.showOrders()
               
        if need_to_update_map and self.frame > -1:
            print 'movie call for update map'
            eV = UpdateMap()
            queue.put(eV)    

#        if updateMap and self.frame > -1:
#            eV = UpdateMap()
#            queue.put(eV)

        if self.frame >= self.numframes:
            self.setEndOfMovieState()
#            if not updateMap:
#                eV = UpdateMap()
#                queue.put(eV)
        elif not self.uv.view.movierunning:
            if movedir == 1:
                if self.frame >= self.endatframe:
                    self.view.pguctrl.UpdateMovieControls(self, False)
#                    if not updateMap:
#                        eV = UpdateMap()
#                        queue.put(eV)
            else:
                if self.frame <= self.endatframe:
                    self.view.pguctrl.UpdateMovieControls(self, False)
#                    if not updateMap:
#                        eV = UpdateMap()
#                        queue.put(eV)
                
        else:
            self.view.pguctrl.UpdateMovieControls(self, True)
            
        
                
    def Start(self, visevents):

        self.visevents = visevents

        # need to refresh after restoring to 'movie' save (which was in clientturnresults
        selected_id = None
        self.uv.refreshAllVisSprites()
        self.uv.showOrders()

#        maxnumframes = len(mm)
#        self.numframes = maxnumframes
        self.numframes = self.game.tot_num_pulses
        self.frame = 0              # number of possible frames = numpulses + 1
                                    # numpulses sets of orders.  1st pulse of orders
                                    # takes frame from frame 0 to frame 1.

        eV = UpdateMap()
        queue.put(eV)
        
        self.cleanup_from_last_round()

        self.view.pguctrl.tp.mc.enableMC()
        self.runMovie(self.numframes, normalmovieframedelay)
        
    def cleanup_from_last_round(self):
        for objid in self.deleted_object_ids:
            del self.game.objectIdDict[objid]
        self.deleted_object_ids = []
        
    def setMovieToFrame(self,setframe):
        doEndOfPulseCleanup = True
        self.game.clientresults.setGameToPulse(setframe, self.frame, self.mm, doEndOfPulseCleanup)
        self.uv.refreshAllVisSprites()
        self.frame = setframe
        print 'frame', self.frame
        if self.frame >= self.numframes:
            self.setEndOfMovieState()
        else:
            self.view.pguctrl.UpdateMovieControls(self, False)
            eV = DisAllowOrders()    # turn off ability to give orders
            queue.put(eV)
        
    def runMovie(self, endatframe, framedelay, playsounds = True, updateMap = True):
#        if self.frame >= self.numframes:
#            self.setEndOfMovieState()
        endatframe = int(endatframe)
        if self.frame != endatframe:
            self.endatframe = endatframe
            self.playsounds = playsounds
            wasatmovieend = False
            
            if self.uv.view.atmovieend and self.game.Time != 0:
                wasatmovieend = True
                self.uv.view.atmovieend = False
                self.game.saveandload.restoreSave('movie')
                self.uv.refreshAllVisSprites()
                self.uv.showOrders()
            
            if self.view.mastercontroller.mainmapC.alloworders:            
                eV = DisAllowOrders()    # turn off ability to give orders
                queue.put(eV)
#                ev = ClearSelectionWindow()
#                queue.put(ev)
#                ev = ClearSelectionEvent(False)
#                queue.put(ev)
                
            if framedelay == 0:
                if self.frame < endatframe:
                    movedir = 1
                else:
                    movedir = -1
                        
                for im in range(self.frame,endatframe,movedir):
                    self.runOneFrame(movedir, updateMap)
                    if movedir == -1 and wasatmovieend:
                        self.uv.showOrders()
                    
            else:
                pygame.time.set_timer(SHOW_MOVIEFRAME, framedelay)
                self.uv.view.movierunning = True
                
                
    def pauseMovie(self):
        pygame.time.set_timer(SHOW_MOVIEFRAME, 0)
        self.uv.view.movierunning = False
        self.view.pguctrl.UpdateMovieControls(self, False)
            
    def setEndOfMovieState(self):
#        if self.amhost:
#            ev = RestoreToPostMovieEvent()
#            queue.put(ev)
#            ev = refreshAllSprites(self.uv.game.myteam)
#            queue.put(ev)
#        elif self.firstshowing:
#            ev = PostMovieSaveEvent()
#            queue.put(ev)
#            self.firstshowing = False

        self.game.saveandload.restoreSave('player')
        self.uv.refreshAllVisSprites()
        self.uv.showOrders()
            
        self.uv.view.atmovieend = True
        self.view.pguctrl.UpdateMovieControls(self, False)
        
        eV = AllowOrders()    
        queue.put(eV)
        
    def runOneFrame(self, movedir = 1, updateMap = True):
#        doEndOfPulseCleanup = False
        #self.uv.game.clientresults.setGameToPulse(self.frame + movedir, self.frame, self.mm, doEndOfPulseCleanup, self.Nation)
        self.showMovieFrame(movedir, updateMap)
        
#        for (N,cplayer,mm) in self.Nationlist:
#            self.uv.game.clientresults.setGameToPulse(self.frame + movedir, self.frame, mm, doEndOfPulseCleanup, N)
#            if not cplayer:
#                self.showMovieFrame(movedir, updateMap)
#        self.uv.game.clientresults.endOfPulseCleanup()  # otherwise deleted units wouldn't be handled properly
                                                            # by movie

    def Notify(self, event):

        if isinstance( event, ShowMovieFrame ):
            self.runOneFrame()

        elif isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, PassUnitViewRef ):
            self.uv = event.uvref
            
#        elif isinstance ( event, RunAFrame ):
#            self.runOneFrame()
#            
        elif isinstance( event, SetMovieFrame):
            self.setMovieToFrame(event.newframe)

        elif isinstance( event, RunMovie):
            self.runMovie(event.endatframe, event.framedelay, event.playsounds, event.updateMap)
            
        elif isinstance( event, PauseMovie):
            self.pauseMovie()
            
    # put in EndMovie function, in case user ends movie before playing it all out
    # use the unit.endturnpos and unit.endturnorders data


