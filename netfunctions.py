import Queue
import threading
from network import *
from game import *
from events import *
from gamefunctions import *
from internalconstants import *
import hostgamecalcs as hgc
from copy import deepcopy
#import townscreen as tscr
try:
    import cPickle as pickle
except:
    import pickle


# will both call NWM to send stuff to clients, and do stuff directly to self
class HostNetFunctions():
#    def __init__(self, NWM, mpdata, evManager):
    def __init__(self, NWM, evManager, profname):
        self.NWM = NWM
#        self.mpdata = mpdata
        self.evManager = evManager

        listencats = []
        self.evManager.RegisterListener( self, listencats )

        self.cNWMlist = []
        
        self.profname = profname
        self.cNWMProfDict = {}
        self.cNWMProfDict[self.profname] = -1
        self.cNWMDict = {}

    def addcNWM(self, cNWM, profname):
        self.cNWMlist.append(cNWM)
        self.cNWMProfDict[profname] = cNWM 
        self.cNWMDict[cNWM] = profname

    def givecnf(self, owncnf):
        self.owncnf = owncnf
    #def providegame(self, game):
    #   self.game = game

    #def CreateUnit(self, type, pos, slot):
    def CreateUnit(self, type, slot):
        newunit = self.game.createUnit(type, slot)

        if newunit != None:
            newunit.uid = id(newunit)
        # todo: change so don't send unit data to all clients, just team members
            for N in self.cNWMlist:
                N.callRemote('UnitCreated', newunit.subtype, slot, newunit.pos, newunit.uid)
            #newunit = Unit(nation, team, type)

        '''else:
            print 'not enough funds'    # todo: change this to an in-game message'''

    def CreateCity(self):
        cityloc = self.game.map.PlaceCity()
        newcity = self.game.CreateCity(cityloc)
        newcity.id = id(newcity)

        print 'innetfunc, cc', threading.currentThread()

        # todo: change so don't send unit data to all clients, just team members
        for N in self.cNWMlist:
            N.callRemote('CityCreated', cityloc, newcity.id)

    def assigncities(self):
        numcities = len(self.game.citylist)
        randcitynumlist = range(numcities)
        cityassignments = []
        #print 'rcl', randcitylist
        for n in self.game.nations:
            chosencitynum = random.choice(randcitynumlist)
            cityassignments.append([chosencitynum, n])
            randcitynumlist.remove(chosencitynum)

        self.game.assigncities(cityassignments)
            #nat = self.game.Nations[n]
            #chosencity = self.game.citylist[chosencitynum]
            #chosencity.owner = n
            #nat.citylist.append(chosencity)

        for N in self.cNWMlist:
            N.callRemote('AssignCities', cityassignments)

    def doneSignal(self, profname):
        eV = WaitForAllClients(profname)
        #self.evManager.Post( eV )
        queue.put(eV)

    def receiveOrders(self, profname, ordlist):

#        for charname in self.game.playerschars[profname]:
#            char = self.game.charnameschar[charname]
#            if char.orders:
#                completeOrdersList.append([char.name, char.orders])
                
        for orddat in ordlist:
            charname = orddat[0]
            charorders = orddat[1]
            cid = self.game.charnamesid[charname]
            
            self.game.saves['hostcomplete'].objectIdDict[cid].orders = deepcopy(charorders)
#            self.game.saves['hostcomplete'].charnameschar[charname].orders = charorders
        
#        self.game.saves['hostcomplete'].nation[nationname]['nationorderslist'] = nationordlist
#        self.game.saves['hostcomplete'].nation[nationname]['unitorderslist'] = unitordlist

    def receive_char_order(self, id, neword):
        datatype = 'char_order'
        data = [id, neword]
        for k,v in self.game.charnamesid.iteritems():
            if v == id:
                name = k
                break
        senderprofile = self.game.charsplayer[name]
        self.game.saveandload.restoreSave('hostcomplete')
        obj = self.game.objectIdDict[id]
        obj.append_order(deepcopy(neword), self.game)
        self.game.saveandload.restoreSave('player')
        if senderprofile != self.profname:      # if host prof generated char order, host prof 
                                                # has already processed it
            eV = dataReceivedEvent(datatype, data)
            queue.put(eV)
        for N in self.cNWMlist:
            thisprof = self.cNWMDict[N]
            if thisprof != senderprofile:   # client that sent data has already processed it
                self.hostSendData(datatype, data, thisprof)

    def receive_client_data(self, datatype, data, sender_profile, send_to_all):
        # this is used to modify data for host gamesave based on a client's action.
        # optionally, the same information can be sent to other clients
        self.game.saveandload.restoreSave('hostcomplete')
        
        # don't think using events is suitable here.  What if save gets switched
        # back before event executes?
        
        send_to_local_player = False
        
        if datatype == 'item_added_to_object':
            obj_id = data[0]
            obj = self.game.objectIdDict[obj_id]
            item_id = data[1]
            item = self.game.objectIdDict[item_id]
            loc = data[2]
            slot = data[3]
            obj.add_item(item,loc,slot)
            
        elif datatype == 'item_removed_from_object':
            obj_id = data[0]
            obj = self.game.objectIdDict[obj_id]
            item_id = data[1]
            item = self.game.objectIdDict[item_id]
            loc = data[2]
            slot = data[3]
            obj.remove_item(item,loc,slot)

        elif datatype == 'append_order':
            eval_needed = False
            obj_id = data[0]
            obj = self.game.objectIdDict[obj_id]
            if not obj.orders:
                eval_needed = True
            obj.append_order(deepcopy(data[1]), self.game)
            if self.game.move_mode == 'free':
                if eval_needed:
                    hgc.evaluate_next_order(obj, self.game, need_to_send_orddat = True)
            else:
                print 'netfunctions, receive client data', self.cNWMlist, len(self.cNWMlist)
                # let other adventurers know of new order
                if self.profname != sender_profile:   # order came from an adventurer not on host computer
                                                # so need to send it to player copy of adventurer on host comp
                    send_to_local_player = True
                for N in self.cNWMlist:
                    thisprof = self.cNWMDict[N]
                    if thisprof != sender_profile:   # client that sent data has already processed it
                        self.hostSendData(datatype, data, thisprof)
                    
        elif datatype == 'delete_last_order':
            obj_id = data[0]
            obj = self.game.objectIdDict[obj_id]
            if obj.orders:
                if self.game.move_mode == 'free':
                    obj.delete_last_order_free_move_mode()
                    self.hostSendData('set_new_orders_after_order_deletion', [obj_id, obj.orders], None)
                    # use set new orders to be careful to keep everybody's order list synchronized
                else:
                    obj.delete_last_order_phased()
                    # let other adventurers know of new order
                    if self.profname != sender_profile:   # order came from an adventurer not on host computer
                                                    # so need to send it to player copy of adventurer on host comp
                        send_to_local_player = True
                    for N in self.cNWMlist:
                        thisprof = self.cNWMDict[N]
                        if thisprof != sender_profile:   # client that sent data has already processed it
                            self.hostSendData('delete_last_order', [obj_id], thisprof)
#                    obj.orders.pop()
#                self.game.mobile_obj_actions.set_new_orders(obj.id, obj.orders)
#                self.hostSendData('delete_last_order', [obj_id], None)

        elif datatype == 'host call function':
            source = data[0]
            func_str = data[1]
            other_data = data[2]
            hgc.call_func(source, func_str, other_data, self.game)

        if send_to_all:
            for N in self.cNWMlist:
                thisprof = self.cNWMDict[N]
                if thisprof != sender_profile:   # client that sent data has already processed it
                    self.hostSendData(datatype, data, thisprof)
                    
        self.game.saveandload.restoreSave('player')
        
        if send_to_local_player:
            ev = dataReceivedEvent(datatype, data)
            queue.put(ev)
                
    def hostSendData(self, datatype, data, profile):
        
        if profile and profile != self.profname:
            self.cNWMProfDict[profile].callRemote('dataTrans', datatype, data)
        else:
            # at this point, host profile gets data for sure, either if it was specified profile,
            # or if all profiles will be getting data
            eV = dataReceivedEvent(datatype, data)
            queue.put(eV)
            if not profile: #send to everybody else
                for N in self.cNWMlist:
                    N.callRemote('dataTrans', datatype, data)
                    
        print 'netfunctions, hostSendData', datatype
            
        

    def Notify(self, event):
        if isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, AllInitUnitsCreated):
            for N in self.cNWMdict.values():
                N.callRemote('AllInitUnitsCreated')

        elif isinstance( event, MPChoicesDone_SendToClient):
            for N in self.cNWMdict.values():
                N.callRemote('MPChoices', event.rseed)
                
        elif isinstance( event, HostSendDataEvent):
            # HostSendDataEvent contains event.datatype, event.data, and optionally event.profile
            # which is a specific profile to which to send data
            # if no specific profile, then data is sent to all clients
            self.hostSendData(event.datatype, event.data, event.profile)

        elif isinstance( event, HostCalcsDone):
            
#            self.game.ai.resultsOfAIOrders(event.mm)
            
#            hostnationname = self.game.startdata['nations'][self.game.myslot]
#            hostnatorders = event.natordersdict[hostnationname]
            eV = RoundResolved(event.mm, True)
            queue.put(eV)
            
            for N in self.cNWMlist:
#                N = self.cNWMdict[slot]
#                nationname = self.game.startdata['nations'][slot]
#                print nationname
                N.callRemote('roundResolved', event.mm)

        elif isinstance( event, CreateCityRequest ):
            self.CreateCity()

        elif isinstance( event, AssignCitiesReq):
            self.assigncities()

# will either call NWM to send stuff to host, or will send stuff to self if host
# or possibly send stuff directly to another client (chat, dual control of nation)
class ClientNetFunctions():
#    def __init__(self, NWM, mpdata, evManager, myslot):
    def __init__(self, NWM, evManager, amihost):
        self.NWM = NWM
#        self.mpdata = mpdata
        self.evManager = evManager
#        self.myslot = myslot
        self.amihost = amihost

        listencats = []
        self.evManager.RegisterListener( self, listencats )

        #self.cNWMdict = {}
        self.hnf = 0

    def addhNWM(self, hNWM):
        self.hNWM = hNWM

    #def addcNWM(self, cNWM, slot):
    #   self.cNWMdict[slot] = cNWM

    #def providegame(self, game):
    #   self.game = game

    def givehnf(self, hnf):     # will only be set for cnf of host
        self.hnf = hnf
        
    def dataReceived(self, datatype, data):
        eV = dataReceivedEvent(datatype, data)
        queue.put(eV)

    #def CreateUnitReq(self, type, pos):
    def CreateUnitReq(self, type):
        if not self.amihost:
            #self.hNWM.callRemote("CreateUnit", type, pos, self.myslot)
            self.hNWM.callRemote("CreateUnit", type, self.myslot)
        else:
            #self.hnf.CreateUnit(type, pos, 0)
            self.hnf.CreateUnit(type, 0)

    def UnitCreated(self, type, slot, pos, uid):
        eV = Unitcreated(type, slot, pos, uid)
        queue.put(eV)
        #self.game.createUnit(type, slot, pos, uid)
        #newunit = Unit(nation, team, type, pos, uid)    # makes client copy of new unit
        #self.game.Nations[nation].units.append(newunit)

    def CityCreated(self, pos, cid):
        eV = Citycreated(pos, cid)
        queue.put(eV)
        #self.game.CreateCity(pos, cid)  # makes client copy of new city

    def assignCities(self, cityassignments):
        eV = CitiesAssigned(cityassignments)
        queue.put(eV)
        #self.game.assigncities(cityassignments)  # makes client copy of new city assignments

    def MoveUnitReq(self, unit, pos, selected):
        if not self.amihost:
            self.hNWM.callRemote("MoveUnit", unit.uid, pos, selected)
        else:
            self.hnf.MoveUnit(unit.uid, pos, selected)

    def allInitUnitsCreated(self):
        eV = AllInitUnitsCreated()
        #self.evManager.Post( eV )
        queue.put(eV)

    def mpchoices(self, rseed):
        eV = MPChoicesDone_Client(rseed)
        #self.evManager.Post( eV )
        queue.put(eV)

    def roundresolved(self, mm):
        eV = RoundResolved(mm, False)
        queue.put(eV)
        
    def sendSupplyRoutes(self, nation):
        
        for cityid in nation.citylist:
            cityobj = self.game.citydict[cityid]
            orddata = []
            orddata.append('transfer supply routes')
            orddata.append(cityid)
            orddata.append(cityobj.supplyroutes)
            nation.nationorderslist.append(orddata)

    def distributeOrders(self):
        eV = DisAllowOrders()    # turn off ability to give orders
        queue.put(eV)
        
#        completeOrdersList = []
#        for charname in self.game.playerschars[self.game.myprofname]:
#            charid = self.game.charnamesid[charname]
#            char = self.game.objectIdDict[charid]
#            char.cleanup_after_done_button()
#            if char.orders:
#                completeOrdersList.append([char.name, char.orders])
        
        self.game.saveandload.doDeepcopySave('movie')

        if not self.amihost:
            eV = WaitForAllClients(self.game.myprofname)
            queue.put(eV)
#            self.hNWM.callRemote("SendOrdersToHost", self.game.myprofname, completeOrdersList).addCallback(self.WaitAfterSendingOrders)
        else:
#            self.hnf.receiveOrders(self.game.myprofname, completeOrdersList)

            eV = WaitForAllClients(self.game.myprofname, 'Orders Done')
            queue.put(eV)

    def WaitAfterSendingOrders(self, obj):
        #eV = WaitForAllClients(self.game.myslot, self.game.numclients, 'Orders Done')
        eV = WaitForAllClients(self.game.myprofname)
        queue.put(eV)

    def initialDataReceivedHandling(self, datatype, data):
        if datatype == 'free_move_results':
            eV = FreeMoveResultsEvent(data)    
            queue.put(eV)
        elif datatype == 'set time':
            eV = SetTimeEvent(data)
            queue.put(eV)
#        elif datatype == 'set time':
#            eV = SetTimeEvent(data[0])
#            queue.put(eV)
        elif datatype == 'append_order':
            eV = AppendOrderEvent(data[0], data[1])    # id of char, new order
            queue.put(eV)
#        elif datatype == 'char_order':
#            eV = AppendOrderEvent(data[0], data[1])    # id of char, new order
#            queue.put(eV)
        elif datatype == 'delete_last_order':
            eV = ShowDeleteLastOrderForOtherMobjEvent(data[0])    # id of char
            queue.put(eV)
        elif datatype == 'set_new_orders_after_order_deletion':
            eV = SetNewOrdersAfterOrderDeletionEvent(data[0], data[1])    # id of char, new order
            queue.put(eV)
        elif datatype == 'show_timed_message':
            eV = ShowTimedMessageEvent(data[0],data[1]) # msg, whether to add to msg list
            queue.put(eV)
        elif datatype == 'new_item_created':
            item_data = pickle.loads(data)
            eV = NewItemCreatedEvent(item_data)
            queue.put(eV)
        elif datatype == 'item_added_to_object':
            eV = HostAddedItemToObjectEvent(data)
            queue.put(eV)
        elif datatype == 'item_removed_from_object':
            eV = HostRemovedItemFromObjectEvent(data)
            queue.put(eV)
        elif datatype == 'all_lighting_data':            
            eV = SetAllLightingEvent(data)
            queue.put(eV)
        elif datatype == 'set_all_tiles_within_party_view':
            eV = SetAllTilesWithinPartyViewEvent(data)
            queue.put(eV)
        elif datatype == 'initscreendone':
            eV = InitScreenDoneEvent()
            queue.put(eV)
        elif datatype == 'townprepared':
            eV = FillTownEvent(data)
            queue.put(eV)
        elif datatype == 'fullencounterdata':
            enc_data = pickle.loads(data)
            eV = SetEncounterDataEvent(enc_data)
            queue.put(eV)
        elif datatype == 'buildmapevent':
            eV = BuildMapEvent()
            queue.put(eV)
        elif datatype == 'assign_imported_object_ids':            
            eV = AssignImportedObjectIdsEvent(data)
            queue.put(eV)
        elif datatype == 'set_vis':            
            eV = SetVisEvent(data)
            queue.put(eV)
#        elif datatype == 'view_level_changes':            
#            eV = ChangeViewLevelsEvent(data)
#            queue.put(eV)
            
            
#        elif datatype == 'switchtoencountermode':
#            eV = SwitchToEncounterModeEvent()
#            queue.put(eV)
            

    def send_char_order(self, id, neword):
        if not self.amihost:
            self.hNWM.callRemote("send_char_order_to_host", id, neword)
        else:                
            self.hnf.receive_char_order(id, neword)
            
    def send_client_data_to_host(self, datatype, data, profile, send_to_all):
        if not self.amihost:
            self.hNWM.callRemote("send_client_data_to_host", datatype, data, profile, send_to_all)
        else:                
            self.hnf.receive_client_data(datatype, data, profile, send_to_all)
            
            
    def Notify(self, event):
        if isinstance( event, PassGameRefEvent ):
            self.game = event.game

        elif isinstance( event, CreateUnitRequest ):
            #self.CreateUnitReq(event.type, event.pos)
            self.CreateUnitReq(event.type)

#       elif isinstance( event, SendDoneCreatingSignal):
#           self.hNWM.callRemote("DoneCreating", event.slot)

        elif isinstance( event, SendDoneSignal):
            self.hNWM.callRemote("DoneSignal", event.profname)

        elif isinstance( event, UnitMoveRequest ):
            self.MoveUnitReq( event.unit, event.pos, event.selected )

        elif isinstance( event, OrdersDone ):
            self.distributeOrders()
            
        elif isinstance(event, dataReceivedEvent):
            self.initialDataReceivedHandling(event.datatype, event.data)
            
        elif isinstance(event, SendCharOrderFromClientEvent):
            self.send_char_order(event.id, event.neword)
            
        elif isinstance(event, SendDataFromClientToHostEvent):
            self.send_client_data_to_host(event.datatype, event.data, event.profile, event.send_to_all)
            




