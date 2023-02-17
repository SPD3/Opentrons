from opentrons import protocol_api

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Eject Tip',
    'description': '''This protocol is only supposed to eject the tip from the 
                       end of a P20 gen2 pipette.''',
    'author': 'Sean Doyle'
    }

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_20ul', 8)
    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 5)

    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tips])
    p20.transfer(20, reservoir['A1'], reservoir['A1'])
    