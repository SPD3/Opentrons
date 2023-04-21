
from opentrons import protocol_api

from typing import List, Optional, Union
from opentrons import protocol_api
from opentrons.types import Location
from opentrons.protocol_api.instrument_context import InstrumentContext
from opentrons.protocol_api import labware

from opentrons.protocol_api.labware import Well

class ReverseTipPickUpDirection(labware.Labware):
    def __init__(self, labware: labware.Labware) -> None:
        super().__init__(core= labware._core,
            api_version= labware._api_version,
            protocol_core= labware._protocol_core,
            core_map= labware._core_map)
        
        labware_cpy = self
        next_tip = super().next_tip()
        self.tips_order = []
        i = 0
        while(next_tip):
            self.tips_order.append(next_tip)
            labware_cpy.use_tips(next_tip)
            next_tip = super().next_tip()
            
            i += 1

        self.tips_order.reverse()
        self.current_tip_index = 0
    
    """Does not care about num_tips or starting_tip"""
    def next_tip(
        self, num_tips: int = 1, starting_tip: Optional[Well] = None
    ) -> Optional[Well]:
        if self.current_tip_index >= len(self.tips_order):
            return None
        current_tip = self.tips_order[self.current_tip_index]
        self.current_tip_index += 1
        return current_tip

class EightToSingleChannelPipette(InstrumentContext):
    def __init__(self, protocol : protocol_api.ProtocolContext, instrument_context: InstrumentContext) -> None:
        super().__init__(core=instrument_context._core, 
                         protocol_core = instrument_context._protocol_core,
                         broker=instrument_context._broker, 
                         api_version=instrument_context._api_version, 
                         tip_racks=instrument_context.tip_racks, 
                         trash=instrument_context.trash_container,
                         requested_as= instrument_context.requested_as)
        for i, tip_rack in enumerate(self.tip_racks):
            self.tip_racks[i] = ReverseTipPickUpDirection(tip_rack)

    @property  # type: ignore
    def channels(self) -> int:
        """The number of channels on the pipette."""
        return 1

    def pick_up_tip(self, location: Optional[Union[Location, labware.Well]] = None, presses: Optional[int] = None, increment: Optional[float] = None, prep_after: Optional[bool] = None) -> InstrumentContext:
        """Defaults presses to 1, as that tends to work best for the 8-1 channel"""
        if not presses:
            presses = 1
        return super().pick_up_tip(location, presses, increment, prep_after)

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Serial Dilution Tutorial',
    'description': '''This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate. This protocol also demonstrates the
                   use of the 8 to 1 channel pipette''',
    'author': 'Sean Doyle'
    }

def get_pipette(protocol : protocol_api.ProtocolContext, name: str, mount:str, tip_racks: List[labware.Labware]) -> InstrumentContext:
    if name == "p10_multi":
        return EightToSingleChannelPipette(
            protocol,
            protocol.load_instrument(
                name,
                mount=mount,
                tip_racks= tip_racks
            )
        )
    return protocol.load_instrument(
            name,
            mount=mount,
            tip_racks= tip_racks
    )

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 5)
    plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 6)

    pipette = protocol.load_instrument('p10_multi', 'right', tip_racks=[tips])
    pipette = EightToSingleChannelPipette(
        protocol,
        pipette
    )

    pipette.transfer(100, reservoir['A1'], plate.wells())
