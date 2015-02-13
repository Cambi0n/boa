import random
from copy import deepcopy
import pygame

from userconstants import *
from saveload import *
from gamefunctions import *
from internalconstants import *
import hostgamecalcs as hgc

class AIDecisions:
    def __init__(self, game):
        self.game = game
        self.last_time_called = 0
        
    def order_all_moves(self):        # normally, this will be a utility function to create a single units move order
#        self.game.saveandload.restoreSave('hostcomplete')
        do_orders = False
        if self.game.move_mode == 'free':
            if self.game.Time - self.last_time_called >= 2000:
                self.last_time_called = self.game.Time
                do_orders = True
        else:
            do_orders = True
            
#        orddat_list = []    # orders that need to go out to clients
        if do_orders:
            
            for section_name in self.game.map_section_names:
                for mid in self.game.map_data[section_name]['monsters']:
                    mon = self.game.objectIdDict[mid]
                    if mon.can_choose_orders():
                        hgc.clear_existing_timed_orders_for_id(mid, self.game)
                        self.order_move_to_nearest(mid)
#                    if orddat:
#                        orddat_list.append(orddat)
                
#        return orddat_list
    
    def find_nearest_vis_enemy(self, mid):
        mon = self.game.objectIdDict[mid]
        lowest_cost = 1000000
        use_path = []
        target = None
        for charid in self.game.charnamesid.itervalues():
            if charid in mon.visible_otherteam_ids:
                char = self.game.objectIdDict[charid]
                if char.map_section == mon.map_section:
                    path, cost = aStar(mon.pos, char.pos, mon, self.game, mon.map_section, move_adjacent = True)
                    if cost < lowest_cost:
                        lowest_cost = cost
                        use_path = deepcopy(path)
                        target = charid
#        if len(use_path) >= 1:
#            use_path.pop()      # remove player square
        return use_path, target, lowest_cost
    
    def order_move_to_nearest(self,mid):
#        orddat = []    
        print 'ai, moving to nearest'
        use_path, target, cost = self.find_nearest_vis_enemy(mid)
        print 'ai, moving2', use_path, target
        if use_path:
            mon = self.game.objectIdDict[mid]
            if self.game.move_mode == 'phased':
                final_tile_idx = find_final_path_idx_within_time(self.game, mon, use_path, seconds_per_round * 1000)
                if final_tile_idx != None:
                    trimmed_path = use_path[0:final_tile_idx+1]
                else:
                    trimmed_path = use_path[0:1]    # can always move 1 square
            else:
                trimmed_path = use_path
            old_ords = deepcopy(mon.orders)   
            new_ords = ['move', trimmed_path]             
            mon.set_new_orders([new_ords], self.game)
            print 'aidecisions, setting orders', new_ords, self.game.move_mode, self.game.saveandload.currentstate
            if not old_ords and self.game.move_mode == 'free':
                hgc.evaluate_next_order(mon, self.game)
            
            
#            orddat = [mon.id, 'set_new_orders_mm', new_ords, old_ords]
#            mon.set_target(target)
#            if self.game.move_mode == 'free':
#                try:
#                    if old_ords[0][0] == 'move':
#                        if old_ords[0][1][0] != use_path[0]:
#                            time_req = find_time_to_next_move(self.game,mon,use_path[0])
#                            new_timed_order = [ (self.game.Time + time_req, ['move', use_path[0]]) ]
#                            hgc.change_next_scheduled_monster_action(mon, new_timed_ord, self.game)
#                except IndexError:
#                    time_req = find_time_to_next_move(self.game,mon,use_path[0])
#                    new_timed_order = [ (self.game.Time + time_req, ['move', use_path[0]]) ]
#                    hgc.change_next_scheduled_monster_action(mon, new_timed_ord, self.game)
                
#        return orddat
    
    def find_monsters_with_target(self,target_id):
        mon_list = []
        for section_name in self.game.map_section_names:
            for mid in self.game.map_data[section_name]['monsters']:
                mon = self.game.objectIdDict[mid]
                if mon.target == target_id:
                    mon_list.append(mid)
        return mon_list
    
    def reorder_monsters_due_to_player_move(self,mover_id):
        # todo - check to see if this target is now closer than current target?
        # becomes the same as order_all_moves I think
        
        for section_name in self.game.map_section_names:
            for mid in self.game.map_data[section_name]['monsters']:
                mon = self.game.objectIdDict[mid]
                mover = self.game.objectIdDict[mover_id]
                if mover.map_section == mon.map_section:
                    cost_to_targ = 1000000
                    cost_to_mover = 1000000
                    if mover_id in mon.visible_otherteam_ids:
                        mpath, cost_to_mover = aStar(mon.pos, mover.pos, mon, self.game, mon.map_section, move_adjacent = True)
                    if mon.target != mover_id:
                        targ = self.game.objectIdDict[mon.target]
                        tpath, cost_to_targ = aStar(mon.pos, targ.pos, mon, self.game, mon.map_section, move_adjacent = True)
                        
                        if mon.target != mover_id:
                            if cost_to_mover < cost_to_targ:
                                pass
                                
                        else:
                            self.order_move_to_nearest(mid)
                                
                    
                        


        
        orddat_list = []
        mon_list = self.find_monsters_with_target(target_id)
        for mid in mon_list:
            orddat = self.order_move(mid)
            if orddat:
                orddat_list.append(orddat)
                
        return orddat_list
        
#        for i in range(self.numcomplayers):
#            self.game.saveandload.restoreSave(self.savenames[i])            
#            nationname = self.nationnames[i]
#            uids = self.game.Nations[nationname].units
#            for uid in uids:
#                u = self.game.objectIdDict[uid]
#                if not u.orders:
#                    newtargx = random.randrange(self.game.mapdim[0])
#                    newtargy = random.randrange(self.game.mapdim[1])
#                    if (newtargx,newtargy) != u.pos:
#                        stm = u.mode['stealth']
#                        sem = u.mode['searching']
#                        newpath, totaltime = aStar(u.pos,(newtargx,newtargy),u, self.game, stm, sem)
#                        
#                        u.orders.append( ['move', newpath] )
#                        
#            self.DistributeAIOrders(nationname,hnf,self.savenames[i])
#            
#        self.game.saveandload.restoreSave('player')            

                        
    def DistributeAIOrders(self,nationname,hnf,savename):                        
#        for i in self.compslots:
#            nationname = self.data['nations'][i]
            nation = self.game.Nations[nationname] 
            nationOrdersList = deepcopy(nation.nationorderslist)
            self.game.saves[savename].nation[nationname]['nationorderslist'] = []

            completeOrdersList = []
            moidlist = nation.movableObjects
            for moid in moidlist:
                mo = self.game.objectIdDict[moid]
                if mo.orders:
                    completeOrdersList.append([mo.id, mo.orders])
                    
            hnf.receiveOrders(nationname,completeOrdersList,nationOrdersList)
            
    def resultsOfAIOrders(self, mm):     
        for i in range(self.numcomplayers):
            
            self.game.saveandload.restoreSave(self.savenames[i])
                        
            nationname = self.nationnames[i]
#        for cs in self.compslots:
#            nationname = self.data['nations'][cs]
            nation = self.game.Nations[nationname]
            
            print 'in ai, results of ai orders', mm[nationname] 

            self.game.clientresults.setGameToPulse(int(numpulses), 0, mm[nationname], False, nation)

        self.game.saveandload.restoreSave('player')            
