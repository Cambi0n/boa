
import carried_object

class Weapon(carried_object.CarriedObject):
    def __init__(self,**params):
        
        params.setdefault('type','weapon')
        params.setdefault('equippable',True)
        params.setdefault('allowed_slots',['mainhand','bothhands','offhand'])
        
        crit_data = {}
        crit_data['range'] = [20]
        crit_data['damage_mult'] = 2.0
        params.setdefault('critical',crit_data)
        self.critical = params['critical']
        
        params.setdefault('reach',False)
        self.reach = params['reach']
        params.setdefault('weapon_size','Medium')
        self.weapon_size = params['weapon_size']
        carried_object.CarriedObject.__init__(self,**params)
        

#        params.setdefault('damage1','1d6')
#        self.damage1 = params['damage1']
#        
#        params.setdefault('damage1type','slash')
#        self.damage1type = params['damage1type']
#        
#        params.setdefault('damage2',None)
#        self.damage2 = params['damage2']
#        
#        params.setdefault('damage2type','slash')
#        self.damage2type = params['damage2type']
        
#        params.setdefault('numhands',1)
#        self.numhands = params['numhands']
#        
#        params.setdefault('offhand_allowed',False)
#        self.offhand_allowed = params['offhand_allowed']
        