from typing import Optional, Union
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