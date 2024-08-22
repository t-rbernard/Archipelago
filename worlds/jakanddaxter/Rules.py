import math
import typing
from BaseClasses import MultiWorld, CollectionState
from . import JakAndDaxterWorld
from .JakAndDaxterOptions import JakAndDaxterOptions, EnableOrbsanity
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
