from opentrons import protocol_api
from opentrons import types

class MyLocation (types.Location):
    def __init__(self, location):
        super().__init__(location.point, location.labware)

    def hi():
        print("hi")

    def __add__(self, o):
        point = types.Point(self._point.x + o._point.x, self._point.y + o._point.y, self._point.z)
        location = types.Location(point, self._labware)
        return MyLocation(location)
    
    def __sub__(self, o):
        point = types.Point(self._point.x - o._point.x, self._point.y - o._point.y, self._point.z)
        location = types.Location(point, self._labware)
        return MyLocation(location)


metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Single tip pick up',
    'description': '''This protocol is supposed to pick up a single tip with the 
        multi-channel p10 pipette.''',
    'author': 'Sean Doyle'
    }


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_20ul', 11)
    p10 = protocol.load_instrument('p10_multi', 'right', tip_racks=[tips])
    #p10.pick_up_tip(MyLocation(tips['A1'].center()) + (MyLocation(tips['A1'].center()) - MyLocation(tips['H1'])))
    p10.pick_up_tip(tips['H1']);
    p10.drop_tip()