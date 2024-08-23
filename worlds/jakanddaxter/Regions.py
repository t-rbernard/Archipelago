import typing
from typing import Dict, TypedDict, Union, Optional

from BaseClasses import MultiWorld, CollectionState, ItemClassification
from Options import OptionError
from . import JakAndDaxterWorld
from .JakAndDaxterOptions import (JakAndDaxterOptions,
                                  EnableMoveRandomizer,
                                  EnableOrbsanity,
                                  FireCanyonCellCount,
                                  MountainPassCellCount,
                                  LavaTubeCellCount,
                                  CompletionCondition)
from .Items import (JakAndDaxterItem,
                    item_table,
                    move_item_table)
from .locs import (CellLocations as Cells,
                   ScoutLocations as Scouts)
from .regs.RegionBase import JakAndDaxterRegion
from .regs import (GeyserRockRegions as GeyserRock,
                   SandoverVillageRegions as SandoverVillage,
                   ForbiddenJungleRegions as ForbiddenJungle,
                   SentinelBeachRegions as SentinelBeach,
                   MistyIslandRegions as MistyIsland,
                   FireCanyonRegions as FireCanyon,
                   RockVillageRegions as RockVillage,
                   PrecursorBasinRegions as PrecursorBasin,
                   LostPrecursorCityRegions as LostPrecursorCity,
                   BoggySwampRegions as BoggySwamp,
                   MountainPassRegions as MountainPass,
                   VolcanicCraterRegions as VolcanicCrater,
                   SpiderCaveRegions as SpiderCave,
                   SnowyMountainRegions as SnowyMountain,
                   LavaTubeRegions as LavaTube,
                   GolAndMaiasCitadelRegions as GolAndMaiasCitadel)


def create_regions(world: JakAndDaxterWorld, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    menu = JakAndDaxterRegion("Menu", player, multiworld)
    multiworld.regions.append(menu)

    # Build the special "Free 7 Scout Flies" Region. This is a virtual region always accessible to Menu.
    # The Locations within are automatically checked when you receive the 7th scout fly for the corresponding cell.
    free7 = JakAndDaxterRegion("'Free 7 Scout Flies' Power Cells", player, multiworld)
    free7.add_cell_locations(Cells.loc7SF_cellTable.keys())
    for scout_fly_cell in free7.locations:

        # Translate from Cell AP ID to Scout AP ID using game ID as an intermediary.
        scout_fly_id = Scouts.to_ap_id(Cells.to_game_id(typing.cast(int, scout_fly_cell.address)))
        scout_fly_cell.access_rule = lambda state, flies=scout_fly_id: state.has(item_table[flies], player, 7)
    multiworld.regions.append(free7)
    menu.connect(free7)

    # If Global Orbsanity is enabled, build the special Orbsanity Region. This is a virtual region always
    # accessible to Menu. The Locations within are automatically checked when you collect enough orbs.
    if options.enable_orbsanity == EnableOrbsanity.option_global:
        orbs = JakAndDaxterRegion("Orbsanity", player, multiworld)

        bundle_size = options.global_orbsanity_bundle_size.value
        bundle_count = 2000 // bundle_size
        for bundle_index in range(bundle_count):

            # Unlike Per-Level Orbsanity, Global Orbsanity Locations always have a level_index of 16.
            orbs.add_orb_locations(16,
                                   bundle_index,
                                   access_rule=lambda state, bundle=bundle_index:
                                   world.count_reachable_orbs(state, "") >= (bundle_size * (bundle + 1)))
        multiworld.regions.append(orbs)
        menu.connect(orbs)

    # Build all regions. Include their intra-connecting Rules, their Locations, and their Location access rules.
    [gr] = GeyserRock.build_regions("Geyser Rock", world, multiworld, options, player)
    [sv] = SandoverVillage.build_regions("Sandover Village", world, multiworld, options, player)
    [fj, fjp] = ForbiddenJungle.build_regions("Forbidden Jungle", world, multiworld, options, player)
    [sb] = SentinelBeach.build_regions("Sentinel Beach", world, multiworld, options, player)
    [mi] = MistyIsland.build_regions("Misty Island", world, multiworld, options, player)
    [fc] = FireCanyon.build_regions("Fire Canyon", world, multiworld, options, player)
    [rv, rvp, rvc] = RockVillage.build_regions("Rock Village", world, multiworld, options, player)
    [pb] = PrecursorBasin.build_regions("Precursor Basin", world, multiworld, options, player)
    [lpc] = LostPrecursorCity.build_regions("Lost Precursor City", world, multiworld, options, player)
    [bs] = BoggySwamp.build_regions("Boggy Swamp", world, multiworld, options, player)
    [mp, mpr] = MountainPass.build_regions("Mountain Pass", world, multiworld, options, player)
    [vc] = VolcanicCrater.build_regions("Volcanic Crater", world, multiworld, options, player)
    [sc] = SpiderCave.build_regions("Spider Cave", world, multiworld, options, player)
    [sm] = SnowyMountain.build_regions("Snowy Mountain", world, multiworld, options, player)
    [lt] = LavaTube.build_regions("Lava Tube", world, multiworld, options, player)
    [gmc, fb, fd] = GolAndMaiasCitadel.build_regions("Gol and Maia's Citadel", world, multiworld, options, player)

    # Configurable counts of cells for connector levels.
    fc_count = options.fire_canyon_cell_count.value
    mp_count = options.mountain_pass_cell_count.value
    lt_count = options.lava_tube_cell_count.value

    # Define the interconnecting rules.
    menu.connect(gr)
    gr.connect(sv)  # Geyser Rock modified to let you leave at any time.
    sv.connect(fj)
    sv.connect(sb)
    sv.connect(mi, rule=lambda state: state.has("Fisherman's Boat", player))
    sv.connect(fc, rule=lambda state: state.has("Power Cell", player, fc_count))  # Normally 20.
    fc.connect(rv)
    rv.connect(pb)
    rv.connect(lpc)
    rvp.connect(bs)  # rv->rvp/rvc connections defined internally by RockVillageRegions.
    rvc.connect(mp, rule=lambda state: state.has("Power Cell", player, mp_count))  # Normally 45.
    mpr.connect(vc)  # mp->mpr connection defined internally by MountainPassRegions.
    vc.connect(sc)
    vc.connect(sm, rule=lambda state: state.has("Snowy Mountain Gondola", player))
    vc.connect(lt, rule=lambda state: state.has("Power Cell", player, lt_count))  # Normally 72.
    lt.connect(gmc)  # gmc->fb connection defined internally by GolAndMaiasCitadelRegions.

    # Set the completion condition.
    if options.jak_completion_condition == CompletionCondition.option_cross_fire_canyon:
        multiworld.completion_condition[player] = lambda state: state.can_reach(rv, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_cross_mountain_pass:
        multiworld.completion_condition[player] = lambda state: state.can_reach(vc, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_cross_lava_tube:
        multiworld.completion_condition[player] = lambda state: state.can_reach(gmc, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_defeat_dark_eco_plant:
        multiworld.completion_condition[player] = lambda state: state.can_reach(fjp, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_defeat_klaww:
        multiworld.completion_condition[player] = lambda state: state.can_reach(mp, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_defeat_gol_and_maia:
        multiworld.completion_condition[player] = lambda state: state.can_reach(fb, "Region", player)

    elif options.jak_completion_condition == CompletionCondition.option_open_100_cell_door:
        multiworld.completion_condition[player] = lambda state: state.can_reach(fd, "Region", player)

    else:
        raise OptionError(f"Unknown completion goal ID ({options.jak_completion_condition.value}).")


# As a sanity check on these options, verify that we have enough locations to allow us to cross
# the connector levels. E.g. if you set Fire Canyon count to 99, we may not have 99 Locations in hub 1.
def verify_connector_level_accessibility(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Set up a fake_state where we only have the items we need to progress, exactly when we need them, as well as
    # any items we would have/get from our other options. The only variable we're actually testing here is the
    # number of power cells we need.
    fake_state = CollectionState(multiworld)
    if options.enable_move_randomizer == EnableMoveRandomizer.option_false:
        for move in move_item_table:
            fake_state.collect(JakAndDaxterItem(move_item_table[move], ItemClassification.progression, move, player))

    class Threshold(TypedDict):
        option: Union[FireCanyonCellCount, MountainPassCellCount, LavaTubeCellCount]
        required_items: Optional[Dict[int, str]]

    thresholds: Dict[int, Threshold] = {
        0: {
            "option": options.fire_canyon_cell_count,
            "required_items": {},
        },
        1: {
            "option": options.mountain_pass_cell_count,
            "required_items": {
                33: "Warrior's Pontoons",
                10945: "Double Jump",
            },
        },
        2: {
            "option": options.lava_tube_cell_count,
            "required_items": {},
        },
    }

    loc = 0
    for k in thresholds:
        option = thresholds[k]["option"]
        required_items = thresholds[k]["required_items"]

        # Given our current fake_state (starting with 0 Power Cells), determine if there are enough
        # Locations to fill with the number of Power Cells needed for the next threshold.
        locations_available = multiworld.get_reachable_locations(fake_state)
        if len(locations_available) < option.value:
            raise OptionError(f"Option conflict with {option.display_name}: "
                              f"not enough potential locations ({len(locations_available)}) "
                              f"for the required number of power cells ({option.value}).")

        # Once we've determined we can pass the current threshold, add what we need to reach the next one.
        new_cells = option.value - fake_state.count("Power Cell", player)
        for _ in range(new_cells):
            fake_state.collect(JakAndDaxterItem("Power Cell", ItemClassification.progression, loc, player))
            loc += 1

        for item in required_items:
            fake_state.collect(JakAndDaxterItem(required_items[item], ItemClassification.progression, item, player))
