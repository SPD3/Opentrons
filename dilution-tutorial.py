from opentrons import protocol_api

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Serial Dilution Tutorial',
    'description': '''This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.''',
    'author': 'Sean Doyle'
    }

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 2)
    plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 3)

    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips])

    p300.transfer(100, reservoir['A1'], plate.wells())

    for i in range(8):
        row = plate.rows()[i]
        p300.transfer(100, reservoir['A2'], row[0], mix_after=(3, 50))
        p300.transfer(100, row[:11], row[1:], mix_after= (3, 50))

