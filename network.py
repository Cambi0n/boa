from twisted.spread import pb
import threading

class HostNetworkManager(pb.Referenceable):
    def __init__(self):
        pass

    def givehnf(self, hnf):
        self.hnf = hnf

    def remote_CreateUnit(self, type, slot):
        self.hnf.CreateUnit(type, slot)

    def remote_MoveUnit(self, uid, pos, selected):
        self.hnf.MoveUnit(uid, pos, selected)

#   def remote_DoneCreating(self, slot):
#       self.hnf.DoneCreating(slot)

    def remote_DoneSignal(self, slot):
        self.hnf.doneSignal(slot)

    def remote_SendOrdersToHost(self, pn, ol):
        self.hnf.receiveOrders(pn, ol)

    def remote_send_char_order_to_host(self, name, neword):
        self.hnf.receive_char_order(name, neword)

    def remote_send_client_data_to_host(self, datatype, data, profile, send_to_all):
        self.hnf.receive_client_data(datatype, data, profile, send_to_all)

class ClientNetworkManager(pb.Referenceable):
    def __init__(self):
        pass

    def givecnf(self, cnf):
        self.cnf = cnf

    def remote_UnitCreated(self, type, slot, pos, uid):
        self.cnf.UnitCreated(type, slot, pos, uid)

    def remote_CityCreated(self, pos, cid):
        print 'innetwork', threading.currentThread()
        self.cnf.CityCreated(pos, cid)

    def remote_AssignCities(self, cityassignments):
        self.cnf.assignCities(cityassignments)

    def remote_UnitMoved(self, uid, pos, selected):
        self.cnf.UnitMoved(uid, pos, selected)

    def remote_AllInitUnitsCreated(self):
        self.cnf.allInitUnitsCreated()

    def remote_MPChoices(self, rseed):
        self.cnf.mpchoices(rseed)

    def remote_roundResolved(self, mm):
        self.cnf.roundresolved(mm)

    def remote_dataTrans(self, datatype, data):
        self.cnf.dataReceived(datatype, data)




