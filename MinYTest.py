import copy
import types
from typing import List, Optional, Union
from opentrons import protocol_api
from opentrons.types import Location
from opentrons.protocols.geometry.deck_conflict import DeckConflictError
from opentrons import types
import math
from opentrons.protocol_api.instrument_context import InstrumentContext
from opentrons.protocol_api.labware import Labware
from opentrons.protocol_api import labware

from opentrons.protocol_api.core.instrument import AbstractInstrument
from opentrons.protocol_api.core.well import AbstractWellCore
from opentrons.protocol_api.protocol_context import ProtocolContext
from opentrons.broker import Broker
from opentrons.protocols.api_support.types import APIVersion
from opentrons.protocol_api.labware import Well

class ReverseTipPickUpDirection(labware.Labware):
    def __init__(self, labware: labware.Labware) -> None:
        super().__init__(implementation = labware._implementation, 
                         api_level = labware._api_version)

class EightToSingleChannelPipette(InstrumentContext):
    def __init__(self, protocol : protocol_api.ProtocolContext, instrument_context: InstrumentContext) -> None:
        super().__init__(implementation=instrument_context._implementation, 
                         ctx=instrument_context._ctx, 
                         broker=instrument_context._broker, 
                         at_version=instrument_context._api_version, 
                         tip_racks=instrument_context.tip_racks, 
                         trash=instrument_context._trash)
        for i, tip_rack in enumerate(self.tip_racks):
            self.tip_racks[i] = ReverseTipPickUpDirection(tip_rack)
        
        self.lowest_y_point = -2000

        # try:
        #     self.lowest_y_point = protocol.load_labware('opentrons_96_tiprack_20ul', 3).next_tip().top().point.y
        #     protocol.
        #     self.lowest_y_point = protocol.load_labware('opentrons_96_tiprack_20ul', 2)
        #     self.lowest_y_point = protocol.load_labware('opentrons_96_tiprack_20ul', 1)

        # except DeckConflictError:
        #     print("Uh Oh")
        #     raise RuntimeError("The multi-to-single channel pipette cannot reach any labware at deck positions 1,2, or 3." + str(type(e)))

    @property  # type: ignore
    def channels(self) -> int:
        """The number of channels on the pipette."""
        return 1

    def pick_up_tip(self, location: Optional[Union[Location, labware.Well]] = None, presses: Optional[int] = None, increment: Optional[float] = None, prep_after: Optional[bool] = None) -> InstrumentContext:
        if not presses:
            presses = 1
        return super().pick_up_tip(location, presses, increment, prep_after)
    
    def move_to(self, location: types.Location, force_direct: bool = False, minimum_z_height: Optional[float] = None, speed: Optional[float] = None, publish: bool = True) -> InstrumentContext:
        if location.point.y < self.lowest_y_point:
            raise RuntimeError("The multi-to-single channel pipette cannot reach the y coordinate at location: ", location)
        return super().move_to(location, force_direct, minimum_z_height, speed, publish)


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
    'protocolName': 'Minimum Y test',
    'description': '''This protocol tries to move the pipette to the lowest Y coordinate it can reach''',
    'author': 'Sean Doyle'
    }

def run(protocol: protocol_api.ProtocolContext):

    # a tip rack for our pipette
    tiprack = protocol.load_labware('opentrons_96_tiprack_20ul', 3)

    # set the pipette we will be using
    pipette = get_pipette(protocol, 'p10_multi', 'right', tip_racks=[tiprack])

    pipette.pick_up_tip()
    pipette.drop_tip()

