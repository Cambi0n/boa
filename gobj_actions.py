from events import *
from gamefunctions import *


class GobjActions():
    def __init__(self, game, evManager):
        self.game = game
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        
            
    def Notify(self, event):
        # next 4 events are instant and only ever occur if game.move_mode == 'free'
        # they occur in response to dragging items around in inventory screen (which isn't
        # allowed in phased move mode)
        # above not true any more - bdf 5/13
        if isinstance( event, AddItemToGameObjectEvent ):
            event.obj.add_item(event.item,event.loc,event.slot)
            if self.game.saveandload.currentstate == 'player':
                ev = SendDataFromClientToHostEvent('item_added_to_object', [event.obj.id, event.item.id, event.loc, event.slot],self.game.myprofname,True)
                queue.put(ev)
                
        elif isinstance( event, RemoveItemFromGameObjectEvent ):
            event.obj.remove_item(event.item,event.loc,event.slot)
            if self.game.saveandload.currentstate == 'player':
                ev = SendDataFromClientToHostEvent('item_removed_from_object', [event.obj.id, event.item.id, event.loc, event.slot],self.game.myprofname,True)
                queue.put(ev)
            
        elif isinstance( event, HostAddedItemToObjectEvent ):
            data = event.data
            obj = self.game.objectIdDict[data[0]]
            item = self.game.objectIdDict[data[1]]
            print 'gobj_actions, notify', item, item.pos, event.data
            loc = data[2]
            slot = data[3]
            obj.add_item(item,loc,slot)
            
        elif isinstance( event, HostRemovedItemFromObjectEvent ):
            data = event.data
            obj = self.game.objectIdDict[data[0]]
            item = self.game.objectIdDict[data[1]]
            loc = data[2]
            slot = data[3]
            obj.remove_item(item,loc,slot)

            
