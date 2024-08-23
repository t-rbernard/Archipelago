import math
import typing
from BaseClasses import MultiWorld, CollectionState
from Options import OptionError
from . import JakAndDaxterWorld
from .JakAndDaxterOptions import (JakAndDaxterOptions,
                                  EnableOrbsanity,
                                  GlobalOrbsanityBundleSize,
                                  PerLevelOrbsanityBundleSize,
                                  FireCanyonCellCount,
                                  MountainPassCellCount,
                                  LavaTubeCellCount,
                                  CitizenOrbTradeAmount,
                                  OracleOrbTradeAmount)
from .Items import orb_item_table
from .locs import CellLocations as Cells
from .Locations import location_table
from .regs.RegionBase import JakAndDaxterRegion


def set_rules(world: JakAndDaxterWorld, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Per Level Orbsanity: trade logic is orbsanity, reach logic is level.
    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        bundle_size = options.level_orbsanity_bundle_size.value

        world.can_trade = lambda state, required_orbs, required_previous_trade: (
            can_trade_orbsanity(state, player, bundle_size, required_orbs, required_previous_trade))

        world.count_reachable_orbs = lambda state, level_name: (
            count_reachable_orbs_level(state, player, multiworld, level_name))

    # Global Orbsanity: trade logic is orbsanity, but reach logic is global.
    elif options.enable_orbsanity == EnableOrbsanity.option_global:
        bundle_size = options.global_orbsanity_bundle_size.value

        world.can_trade = lambda state, required_orbs, required_previous_trade: (
            can_trade_orbsanity(state, player, bundle_size, required_orbs, required_previous_trade))

        world.count_reachable_orbs = lambda state, level_name: (
            count_reachable_orbs_global(state, player, multiworld))

    # No Orbsanity: trade logic is normal, and reach logic is still global (vanilla orbs are all fungible).
    else:
        world.can_trade = lambda state, required_orbs, required_previous_trade: (
            can_trade_regular(state, player, multiworld, required_orbs, required_previous_trade))

        world.count_reachable_orbs = lambda state, level_name: (
            count_reachable_orbs_global(state, player, multiworld))


def count_reachable_orbs_global(state: CollectionState,
                                player: int,
                                multiworld: MultiWorld) -> int:

    accessible_orbs = 0
    for region in multiworld.get_regions(player):
        if state.can_reach_region(region.name, player):
            accessible_orbs += typing.cast(JakAndDaxterRegion, region).orb_count

    return accessible_orbs


def count_reachable_orbs_level(state: CollectionState,
                               player: int,
                               multiworld: MultiWorld,
                               level_name: str = "") -> int:

    accessible_orbs = 0
    regions = typing.cast(typing.List[JakAndDaxterRegion], multiworld.get_regions(player))
    for region in regions:
        if region.level_name == level_name and state.can_reach_region(region.name, player):
            accessible_orbs += region.orb_count

    return accessible_orbs


def can_trade_regular(state: CollectionState,
                      player: int,
                      multiworld: MultiWorld,
                      required_orbs: int,
                      required_previous_trade: typing.Optional[int] = None) -> bool:

    # We know that Orbsanity is off, so count orbs globally.
    accessible_orbs = count_reachable_orbs_global(state, player, multiworld)
    if required_previous_trade:
        name_of_previous_trade = location_table[Cells.to_ap_id(required_previous_trade)]
        return (accessible_orbs >= required_orbs
                and state.can_reach_location(name_of_previous_trade, player=player))
    else:
        return accessible_orbs >= required_orbs


def can_trade_orbsanity(state: CollectionState,
                        player: int,
                        orb_bundle_size: int,
                        required_orbs: int,
                        required_previous_trade: typing.Optional[int] = None) -> bool:

    required_count = math.ceil(required_orbs / orb_bundle_size)
    orb_bundle_name = orb_item_table[orb_bundle_size]
    if required_previous_trade:
        name_of_previous_trade = location_table[Cells.to_ap_id(required_previous_trade)]
        return (state.has(orb_bundle_name, player, required_count)
                and state.can_reach_location(name_of_previous_trade, player=player))
    else:
        return state.has(orb_bundle_name, player, required_count)


def can_free_scout_flies(state: CollectionState, player: int) -> bool:
    return state.has("Jump Dive", player) or state.has_all({"Crouch", "Crouch Uppercut"}, player)


def can_fight(state: CollectionState, player: int) -> bool:
    return state.has_any({"Jump Dive", "Jump Kick", "Punch", "Kick"}, player)


def enforce_multiplayer_limits(options: JakAndDaxterOptions):
    friendly_message = ""

    if options.enable_orbsanity == EnableOrbsanity.option_global:
        if options.global_orbsanity_bundle_size.value < GlobalOrbsanityBundleSize.friendly_minimum:
            friendly_message += (f"  "
                                 f"{options.global_orbsanity_bundle_size.display_name} must be no less than "
                                 f"{GlobalOrbsanityBundleSize.friendly_minimum} (currently "
                                 f"{options.global_orbsanity_bundle_size.value}).\n")

    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        if options.level_orbsanity_bundle_size.value < PerLevelOrbsanityBundleSize.friendly_minimum:
            friendly_message += (f"  "
                                 f"{options.level_orbsanity_bundle_size.display_name} must be no less than "
                                 f"{PerLevelOrbsanityBundleSize.friendly_minimum} (currently "
                                 f"{options.level_orbsanity_bundle_size.value}).\n")

    if options.fire_canyon_cell_count.value > FireCanyonCellCount.friendly_maximum:
        friendly_message += (f"  "
                             f"{options.fire_canyon_cell_count.display_name} must be no greater than "
                             f"{FireCanyonCellCount.friendly_maximum} (currently "
                             f"{options.fire_canyon_cell_count.value}).\n")

    if options.mountain_pass_cell_count.value > MountainPassCellCount.friendly_maximum:
        friendly_message += (f"  "
                             f"{options.mountain_pass_cell_count.display_name} must be no greater than "
                             f"{MountainPassCellCount.friendly_maximum} (currently "
                             f"{options.mountain_pass_cell_count.value}).\n")

    if options.lava_tube_cell_count.value > LavaTubeCellCount.friendly_maximum:
        friendly_message += (f"  "
                             f"{options.lava_tube_cell_count.display_name} must be no greater than "
                             f"{LavaTubeCellCount.friendly_maximum} (currently "
                             f"{options.lava_tube_cell_count.value}).\n")

    if options.citizen_orb_trade_amount.value > CitizenOrbTradeAmount.friendly_maximum:
        friendly_message += (f"  "
                             f"{options.citizen_orb_trade_amount.display_name} must be no greater than "
                             f"{CitizenOrbTradeAmount.friendly_maximum} (currently "
                             f"{options.citizen_orb_trade_amount.value}).\n")

    if options.oracle_orb_trade_amount.value > OracleOrbTradeAmount.friendly_maximum:
        friendly_message += (f"  "
                             f"{options.oracle_orb_trade_amount.display_name} must be no greater than "
                             f"{OracleOrbTradeAmount.friendly_maximum} (currently "
                             f"{options.oracle_orb_trade_amount.value}).\n")

    if friendly_message != "":
        raise OptionError(f"Please adjust the following Options for a multiplayer game.\n"
                          f"{friendly_message}")


def verify_orbs_for_trades(options: JakAndDaxterOptions):

    total_trade_orbs = (9 * options.citizen_orb_trade_amount) + (6 * options.oracle_orb_trade_amount)
    if total_trade_orbs > 2000:
        raise OptionError(f"Required number of orbs for all trades ({total_trade_orbs}) "
                          f"is more than all the orbs in the game (2000). "
                          f"Reduce the value of either {options.citizen_orb_trade_amount.display_name} "
                          f"or {options.oracle_orb_trade_amount.display_name}.")
