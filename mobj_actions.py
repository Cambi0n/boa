
from events import *
from gamefunctions import *
import object_utils


class MobjActions():
    def __init__(self, game, evManager):
        self.game = game
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

    def moveOrder(self, object, pos):
        lop = object.lastOrderedPos
#        if object.objtype != 'movementgroup':
#            lop = object.lastOrderedPos
#        else:
#            firstunit = self.game.objectIdDict[object.allmembers[0]]
#            lop = firstunit.lastOrderedPos
#            object.ordtimesfresh = False
        mapsection = object.lastOrderedMapSection
        newpath, totalcost = aStar(lop, pos, object, self.game, mapsection)
        
        return newpath, totalcost
    
    def delete_last_order(self, obj_id, self_generated = False):
        if self.game.move_mode == 'phased':
            # for phased mode, local client deletes it, then sends to host, then host deletes it, then host
            # sends to other clients and they delete it
            obj = self.game.objectIdDict[obj_id]
            obj.delete_last_order_phased()
            obj.SetLastOrderedPos(obj.find_last_ordered_pos())
            
            obj.recalc_movement_points_remaining(self.game)
            obj.update_actions_used('remove_last_order')
            obj.allowed_move_tiles_fresh = False
            obj.find_allowed_moves_for_mobj(self.game, 'last_ordered')
            print '############## mobj actions, delete last order ##############'
            if self_generated:
                ev = SendDataFromClientToHostEvent('delete_last_order', [obj.id], self.game.myprofname, False)
                queue.put(ev)
                ev = SetAllowedMovesVisualsEvent(obj)
                queue.put(ev)
            eV = ShowOrders()
            queue.put(eV)
            ev = UpdateMap()
            queue.put(ev)
        else:
            # for free mode, local can't just delete it or else might get out of synch, so send deletion to host
            # host deletes it and sends deletion to all clients, including one that originated it
            ev = SendDataFromClientToHostEvent('delete_last_order', [obj.id], self.game.myprofname, True)
            queue.put(ev)
            
#    def just_delete_last_order(self, obj_id):
#        thischar = self.game.objectIdDict[obj_id]
#        thischar.delete_last_order_phased()
            
    def order_move(self, obj, newpath, totalcost):
        neword = ['move', newpath]
        obj.append_order(neword, self.game)
        obj.SetLastOrderedPos(newpath[-1], self.game)
        if self.game.move_mode == 'phased':
            obj.order_use_of_movement_points(totalcost)
            obj.update_actions_used('use_partial_move_action')
            obj.find_allowed_moves_for_mobj(self.game, 'last_ordered')
            if obj.objtype == 'playerchar':
                print '################### mobj actions, order move ###############'
                ev = SetAllowedMovesVisualsEvent(obj)
                queue.put(ev)
            
        ev = SendDataFromClientToHostEvent('append_order', [obj.id, neword], self.game.myprofname, False)
        queue.put(ev)
        eV = ShowOrders()
        queue.put(eV)
            
    def order_spellcast(self, source, data):
        caster_id = source['obj_id']
        caster = self.game.objectIdDict[caster_id]
#        source = {}
#        source['spell_name'] = spell_name
#        source['obj_id'] = caster_id
        neword = ['cast_spell', source, data]
        caster.append_order(neword, self.game)
        if self.game.move_mode == 'phased':
            caster.update_actions_used('use_standard_action')
            # todo - subtract this spell from spells memorized
        
        ev = SendDataFromClientToHostEvent('append_order', [caster_id, neword], self.game.myprofname, False)
        queue.put(ev)
        eV = ShowOrders()
        queue.put(eV)
        
    def order_standard_attack(self,sel_obj,attacked_obj):
        source = {}
        source['obj_id'] = sel_obj.id
        source['attack_type'] = 'melee'
        source['attack_hands'] = 'mainhand'
        neword = ['standard_attack', attacked_obj.id, source]
        sel_obj.append_order(neword, self.game)
#            event.sel_obj.order_use_of_movement_points(totalcost)
#                event.sel_obj.SetLastOrderedPos(event.pos, self.game)
        if self.game.move_mode == 'phased':
            sel_obj.update_actions_used('use_standard_action')
            sel_obj.find_allowed_moves_for_mobj(self.game, 'last_ordered')
            if sel_obj.objtype == 'playerchar':
                print '################ mobj actions order standard attack ################'
                ev = SetAllowedMovesVisualsEvent(sel_obj)
                queue.put(ev)
                
        ev = SendDataFromClientToHostEvent('append_order', [sel_obj.id, neword], self.game.myprofname, False)
        queue.put(ev)
        eV = ShowOrders()
        queue.put(eV)
#        eV = SendCharOrderFromClientEvent(event.sel_obj.id, neword)
#        queue.put(eV)

    def order_drop_item(self, item, holder):
        neword = ['drop item', item.id, False]
        holder.append_order(neword, self.game)
        if self.game.move_mode == 'phased':
            loc = holder.find_loc_of_item(item)
            if loc == 'stored':
                neword = ['drop item', item.id, True]
                holder.update_actions_used('use_move_action')
                holder.allowed_move_tiles_fresh = False
                holder.find_allowed_moves_for_mobj(self.game)
                print '################ mobj actions order drop item ################'
                ev = SetAllowedMovesVisualsEvent(holder)
                queue.put(ev)
                ev = UpdateMap()
                queue.put(ev)
                
                
        ev = SendDataFromClientToHostEvent('append_order', [holder.id, neword], self.game.myprofname, False)
        queue.put(ev)
        
    def order_pickup_item(self, item, holder):
        neword = ['pickup item', item.id, False]
        holder.append_order(neword, self.game)
        if self.game.move_mode == 'phased':
            neword = ['pickup item', item.id, True]
            holder.update_actions_used('use_move_action')
            holder.allowed_move_tiles_fresh = False
            holder.find_allowed_moves_for_mobj(self.game)
            print '################ mobj actions order pickup item ################'
            ev = SetAllowedMovesVisualsEvent(holder)
            queue.put(ev)
            ev = UpdateMap()
            queue.put(ev)
        ev = SendDataFromClientToHostEvent('append_order', [holder.id, neword], self.game.myprofname, False)
        queue.put(ev)
        
    def find_unique_monster_name(self, this_mon, sugg_num = 1):
        name_not_found = True
        try_number = sugg_num
        while name_not_found:
            proposed_name = this_mon.species + ' ' + str(try_number)
            duplicate_found = False
            for map_sec_name in self.game.map_section_names:
                for mid in self.game.map_data[map_sec_name]['monsters']:
                    mon = self.game.objectIdDict[mid]
                    if mon.display_name == proposed_name:
                        duplicate_found = True
                        break
                if duplicate_found:
                    break
            if not duplicate_found:
                name_not_found = False
            else:
                try_number += 1
        return proposed_name

    def add_race_effects_all(self):
        for id in self.game.charnamesid.itervalues():
            obj = self.game.objectIdDict[id]
            self.add_race_effects(obj)
        
    def add_race_effects(self,obj):
        effect_func_str_dict = self.game.dict_of_races[obj.race].effect_func_str_dict
        obj.add_permanent_effect([obj.race,{'race_name':obj.race}], self.game, effect_func_str_dict)
            
    def set_new_orders_after_order_deletion(self, id, newords):
        thischar = self.game.objectIdDict[id]
        if newords:
            thischar.update_actions_used('remove_last_order')
        else:
            thischar.update_actions_used('clear all')
        thischar.set_new_orders(newords, self.game)

        print '################ mobj actions set new orders ################'
        ev = SetAllowedMovesVisualsEvent(thischar)
        queue.put(ev)
        ev = UpdateMap()
        queue.put(ev)
        
        if thischar.objtype == 'playerchar':
            eV = ShowOrders()
            queue.put(eV)
            
    def Notify(self, event):
        if isinstance( event, MoveOrder_Game ):
            if event.pos != event.unit.pos:
                newpath, totalcost = self.moveOrder(event.unit, event.pos) # event.unit may be single object or movement group
                if newpath:
                    self.order_move(event.unit, newpath, totalcost)
#                    if self.game.move_mode == 'phased':
#                        self.execute_phased_move(event.unit, newpath, totalcost)
#                    elif self.game.move_mode == 'free':
#                        self.execute_free_move(event.unit, newpath, totalcost)

                
        elif isinstance( event, AppendOrderEvent ):
            # clients receives this from host after client has successfully requested an order to be appended

#            for cid in self.game.charnamesid.values():
#                c = self.game.objectIdDict[cid]
#                if c.name == event.name:
#                    thischar = c
#                    break

            thischar = self.game.objectIdDict[event.id]
            thischar.append_order(event.neword, self.game)
            eV = ShowOrders()
            queue.put(eV)

        elif isinstance( event, SetNewOrdersAfterOrderDeletionEvent ):
            self.set_new_orders_after_order_deletion(event.id, event.neword)

        elif isinstance( event, OrderDeleteLastOrderEvent):
            self.delete_last_order(event.unit.id, True)

        elif isinstance( event, ShowDeleteLastOrderForOtherMobjEvent):
            self.delete_last_order(event.obj_id)

        elif isinstance( event, FindAllowedMovesEvent ):
            event.object.find_allowed_moves_for_mobj(self.game, event.type)
            
        elif isinstance( event, ChangeObjectsActionModeEvent ):
            event.mobj.change_action_mode(event.new_mode)
            
        elif isinstance( event, AddStandardMeleeAttackOrderEvent ):
            self.order_standard_attack(event.sel_obj, event.attacked_obj)
            
        elif isinstance( event, AddCastOrderEvent ):
            self.order_spellcast(event.source, event.data)

        elif isinstance( event, OrderDropItemToGroundEvent ):
            self.order_drop_item(event.item, event.holder)

        elif isinstance( event, OrderPickupItemFromGroundEvent ):
            self.order_pickup_item(event.item, event.holder)


