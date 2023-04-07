from typing import List, Optional
from opentrons import protocol_api

from opentrons import types
from opentrons.protocol_api.instrument_context import InstrumentContext
from opentrons.protocol_api.labware import Labware
from opentrons.protocol_api import labware
import copy
from opentrons.protocol_api.labware import Well

class ReverseTipPickUpDirection(labware.Labware):
    def __init__(self, labware: labware.Labware) -> None:
        super().__init__(implementation = labware._implementation, 
                         api_level = labware._api_version)
        
        labware_cpy = copy.deepcopy(labware)
        next_tip = labware_cpy.next_tip()
        self.tips_order = []
        i = 0
        while(next_tip):
            self.tips_order.append(next_tip)
            labware_cpy.use_tips(next_tip)
            next_tip = labware_cpy.next_tip()
            
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
        # ctx=self,
        #     broker=self._broker,
        #     implementation=instrument_core,
        #     at_version=self._api_version,
        #     # TODO(mc, 2022-08-25): test instrument tip racks
        #     tip_racks=tip_racks,
        super().__init__(implementation=instrument_context._implementation, 
                         ctx=instrument_context._ctx, 
                         broker=instrument_context._broker, 
                         at_version=instrument_context._api_version, 
                         tip_racks=instrument_context.tip_racks, 
                         trash=instrument_context._trash)
        for i, tip_rack in enumerate(self.tip_racks):
            self.tip_racks[i] = ReverseTipPickUpDirection(tip_rack)

    @property  # type: ignore
    def channels(self) -> int:
        """The number of channels on the pipette."""
        return 1


def get_pipette(protocol : protocol_api.ProtocolContext, name: str, mount:str, tip_racks: List[Labware]) -> InstrumentContext:
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

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Pick up all tips one by one',
    'description': '''This protocol is supposed to pick up all of the tips one 
        by one with the multi-channel p10 pipette.''',
    'author': 'Sean Doyle'
    }

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_20ul', 10)
    p10 = get_pipette(protocol, 'p10_multi', 'right', tip_racks=[tips])
    for i in range(96):
        p10.pick_up_tip()
        p10.drop_tip()