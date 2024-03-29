import copy
from typing import List, Optional, Union
from opentrons import protocol_api
from opentrons.types import Location
import math
from opentrons.protocol_api.instrument_context import InstrumentContext
from opentrons.protocol_api.labware import Labware
from opentrons.protocol_api import labware

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

    def pick_up_tip(self, location: Optional[Union[Location, labware.Well]] = None, presses: Optional[int] = None, increment: Optional[float] = None, prep_after: Optional[bool] = None) -> InstrumentContext:
        """Defaults presses to 1, as that tends to work best for the 8-1 channel"""
        if not presses:
            presses = 1
        return super().pick_up_tip(location, presses, increment, prep_after)

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

TIP_RACK_LOCATION = 10

metadata = {
    'apiLevel': '2.8',
    'protocolName': '8 Channel Multicolor Perimeter',
    'author': 'Tim Dobbs and Counter Culture Labs',
    'source': 'ARTBot Protocol Builder',
    'description': """Protocol for drawing bio-art.
                      Built from a template and the designer
                      at bioartbot.org"""
    }

def distribute_to_agar(pipette, vol, source, destination, disposal_vol):
    max_volume = pipette.max_volume
    needs_new_tip = True

    dest = list(destination)  # allows for non-lists

    for cnt, well in enumerate(dest):
        if (cnt + 1) % 150 == 0:
            needs_new_tip = True

        if pipette.current_volume < (vol + disposal_vol):
            if needs_new_tip:
                if pipette.has_tip: pipette.drop_tip()
                pipette.pick_up_tip()
                needs_new_tip = False
                
            remaining_wells = len(dest) - cnt
            remaining_vol = remaining_wells * vol

            if remaining_vol + disposal_vol > max_volume:
                asp_vol = math.floor((max_volume - disposal_vol) / vol) * vol + disposal_vol - pipette.current_volume
            else:
                asp_vol = remaining_vol + disposal_vol - pipette.current_volume

            pipette.aspirate(asp_vol, source)
            pipette.touch_tip(source, v_offset= -15)
            # if vol < 0.3: 
            #     pipette.touch_tip(source) #avoid blotches from liquid stuck to the outside of the tip

        pipette.move_to(well)
        pipette.dispense(vol)


    pipette.drop_tip()


def run(protocol: protocol_api.ProtocolContext):  
    # a tip rack for our pipette
    tiprack = protocol.load_labware('opentrons_96_tiprack_20ul', TIP_RACK_LOCATION)

    # a plate for all of the colors in our pallette
    palette = protocol.load_labware('cryo_35_tuberack_2000ul', 11)

    # set the pipette we will be using
    pipette = get_pipette(protocol, 'p10_multi', 'right', tip_racks=[tiprack])

    # load all of the 
    pixels_by_color_by_artpiece = {'1': {'multicolor-perimeter#1': [(-0.7071067811865475, 0.7071067811865476, 0.99), (-0.7071067811865475, 0.6505382386916237, 0.99), (-0.7071067811865475, 0.5939696961967, 0.99), (-0.7071067811865475, 0.5374011537017761, 0.99), (-0.7071067811865475, 0.48083261120685233, 0.99), (-0.7071067811865475, 0.42426406871192857, 0.99), (-0.7071067811865475, 0.36769552621700474, 0.99), (-0.7071067811865475, 0.3111269837220809, 0.99), (-0.7071067811865475, 0.25455844122715715, 0.99), (-0.6505382386916236, 0.7071067811865476, 0.99), (-0.5939696961966998, 0.7071067811865476, 0.99), (-0.537401153701776, 0.7071067811865476, 0.99), (-0.4808326112068523, 0.7071067811865476, 0.99), (-0.42426406871192845, 0.7071067811865476, 0.99), (-0.36769552621700463, 0.7071067811865476, 0.99), (-0.3111269837220808, 0.7071067811865476, 0.99), (-0.25455844122715704, 0.7071067811865476, 0.99), (-0.19798989873223327, 0.7071067811865476, 0.99), (-0.1414213562373095, 0.7071067811865476, 0.99), (-0.08485281374238562, 0.7071067811865476, 0.99), (-0.028284271247461846, 0.7071067811865476, 0.99), (0.028284271247461933, 0.7071067811865476, 0.99), (0.0848528137423858, 0.7071067811865476, 0.99)]}, '2': {'multicolor-perimeter#1': [(0.1414213562373095, 0.7071067811865476, 0.99), (0.19798989873223335, 0.7071067811865476, 0.99), (0.2545584412271572, 0.7071067811865476, 0.99), (0.3111269837220809, 0.7071067811865476, 0.99), (0.3676955262170048, 0.7071067811865476, 0.99), (0.42426406871192845, 0.7071067811865476, 0.99), (0.48083261120685233, 0.7071067811865476, 0.99), (0.5374011537017762, 0.7071067811865476, 0.99), (0.5939696961966999, 0.7071067811865476, 0.99), (0.6505382386916237, 0.7071067811865476, 0.99), (0.7071067811865477, 0.7071067811865476, 0.99), (0.7071067811865477, 0.6505382386916237, 0.99), (0.7071067811865477, 0.5939696961967, 0.99), (0.7071067811865477, 0.5374011537017761, 0.99), (0.7071067811865477, 0.48083261120685233, 0.99), (0.7071067811865477, 0.42426406871192857, 0.99), (0.7071067811865477, 0.36769552621700474, 0.99), (0.7071067811865477, 0.3111269837220809, 0.99)]}, '3': {'multicolor-perimeter#1': [(0.7071067811865477, 0.25455844122715715, 0.99), (0.7071067811865477, 0.19798989873223335, 0.99), (0.7071067811865477, 0.1414213562373096, 0.99), (0.7071067811865477, 0.08485281374238571, 0.99), (0.7071067811865477, 0.028284271247461933, 0.99), (0.7071067811865477, -0.028284271247461846, 0.99), (0.7071067811865477, -0.08485281374238571, 0.99), (0.7071067811865477, -0.1414213562373094, 0.99), (0.7071067811865477, -0.19798989873223327, 0.99), (0.7071067811865477, -0.25455844122715715, 0.99), (0.7071067811865477, -0.3111269837220808, 0.99), (0.7071067811865477, -0.3676955262170047, 0.99), (0.7071067811865477, -0.4242640687119284, 0.99), (0.7071067811865477, -0.4808326112068523, 0.99), (0.7071067811865477, -0.5374011537017761, 0.99), (0.7071067811865477, -0.5939696961966998, 0.99), (0.7071067811865477, -0.6505382386916236, 0.99), (0.7071067811865477, -0.7071067811865476, 0.99)]}, '4': {'multicolor-perimeter#1': [(-0.36769552621700463, -0.7071067811865476, 0.99), (-0.3111269837220808, -0.7071067811865476, 0.99), (-0.25455844122715704, -0.7071067811865476, 0.99), (-0.19798989873223327, -0.7071067811865476, 0.99), (-0.1414213562373095, -0.7071067811865476, 0.99), (-0.08485281374238562, -0.7071067811865476, 0.99), (-0.028284271247461846, -0.7071067811865476, 0.99), (0.028284271247461933, -0.7071067811865476, 0.99), (0.0848528137423858, -0.7071067811865476, 0.99), (0.1414213562373095, -0.7071067811865476, 0.99), (0.19798989873223335, -0.7071067811865476, 0.99), (0.2545584412271572, -0.7071067811865476, 0.99), (0.3111269837220809, -0.7071067811865476, 0.99), (0.3676955262170048, -0.7071067811865476, 0.99), (0.42426406871192845, -0.7071067811865476, 0.99), (0.48083261120685233, -0.7071067811865476, 0.99), (0.5374011537017762, -0.7071067811865476, 0.99), (0.5939696961966999, -0.7071067811865476, 0.99), (0.6505382386916237, -0.7071067811865476, 0.99)]}, '5': {'multicolor-perimeter#1': [(-0.7071067811865475, 0.19798989873223335, 0.99), (-0.7071067811865475, 0.1414213562373096, 0.99), (-0.7071067811865475, 0.08485281374238571, 0.99), (-0.7071067811865475, 0.028284271247461933, 0.99), (-0.7071067811865475, -0.028284271247461846, 0.99), (-0.7071067811865475, -0.08485281374238571, 0.99), (-0.7071067811865475, -0.1414213562373094, 0.99), (-0.7071067811865475, -0.19798989873223327, 0.99), (-0.7071067811865475, -0.25455844122715715, 0.99), (-0.7071067811865475, -0.3111269837220808, 0.99), (-0.7071067811865475, -0.3676955262170047, 0.99), (-0.7071067811865475, -0.4242640687119284, 0.99), (-0.7071067811865475, -0.4808326112068523, 0.99), (-0.7071067811865475, -0.5374011537017761, 0.99), (-0.7071067811865475, -0.5939696961966998, 0.99), (-0.7071067811865475, -0.6505382386916236, 0.99), (-0.7071067811865475, -0.7071067811865476, 0.99), (-0.6505382386916236, -0.7071067811865476, 0.99), (-0.5939696961966998, -0.7071067811865476, 0.99), (-0.537401153701776, -0.7071067811865476, 0.99), (-0.4808326112068523, -0.7071067811865476, 0.99), (-0.42426406871192845, -0.7071067811865476, 0.99)]}}
    canvas_locations = {'multicolor-perimeter#1': '5'}
    color_map = {'6': 'red_FC', '7': 'blue_FC', '8': 'green_FC', '10': 'purple_FC', '9': 'orange_FC', '12': 'yellow_FC', '1': 'pink', '3': 'teal', '4': 'peach', '5': 'fluorescent yellow', '2': 'indigo', '13': 'fluorescent green', '14': 'red', '15': 'blue', '16': 'purple', '17': 'orange', '18': 'yellow'}

    # a function that gets us the next available well in a plate
    def well_generator(plate):
        for well in plate.wells():
            yield well
    get_well = well_generator(palette)

    # colored culture locations
    palette_colors = { color: next(get_well) for color in pixels_by_color_by_artpiece.keys() }
    protocol.comment('**CHECK BEFORE RUNNING** - Colors should be loaded into these wells:')
    for color in palette_colors:
        protocol.comment(f'{color_map[color]} -> {palette_colors[color]}')

    # plates to create art in
    canvas_labware = dict()
    for art_title in canvas_locations:
        canvas_labware[art_title] = protocol.load_labware('bioartbot_petriplate_90mm_round', canvas_locations[art_title])

    # wells to dispense each color material to
    pixels_by_color = dict()
    for color in pixels_by_color_by_artpiece:
        pixels_by_color[color] = list()
        pixels_by_artpiece = pixels_by_color_by_artpiece[color]
        for art_title in pixels_by_artpiece:
            pixels_by_color[color] += [
                Location(
                    point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=pixel[2]),
                    labware=canvas_labware[art_title]
                 )
                for pixel in pixels_by_artpiece[art_title]
            ]
            if not len(pixels_by_artpiece[art_title]): #single-well case
                pixel = pixels_by_artpiece[art_title]
                pixels_by_color[color] += [
                    Location(
                        point=canvas_labware[art_title].wells()[0].from_center_cartesian(x=pixel[0], y=pixel[1], z=pixel[2]),
                        labware=canvas_labware[art_title]
                    )
                ]

    for color in pixels_by_color:
        distribute_to_agar(pipette, 0.4, palette_colors[color], pixels_by_color[color], disposal_vol=2)