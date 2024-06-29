import math
import typing
from BaseClasses import MultiWorld, CollectionState
from .JakAndDaxterOptions import JakAndDaxterOptions
from .Items import orb_item_table
from .locs import CellLocations as Cells, OrbLocations as Orbs
from .Locations import location_table
from .regs.RegionBase import JakAndDaxterRegion


def can_reach_orbs(state: CollectionState,
                   player: int,
                   multiworld: MultiWorld) -> int:

    accessible_orbs = 0
    for region in multiworld.get_regions(player):
        if state.can_reach(region, "Region", player):
            accessible_orbs += typing.cast(JakAndDaxterRegion, region).orb_count

    return accessible_orbs


# TODO - Until we come up with a better progressive system for the traders (that avoids hard-locking if you pay the
#  wrong ones and can't afford the right ones) just make all the traders locked behind the total amount to pay them all.
def can_trade(state: CollectionState,
              player: int,
              multiworld: MultiWorld,
              options: JakAndDaxterOptions,
              required_orbs: int,
              required_previous_trade: int = None) -> bool:

    if options.enable_orbsanity.value > 0:
        bundle_size = options.enable_orbsanity.value
        return can_trade_orbsanity(state, player, bundle_size, required_orbs, required_previous_trade)
    else:
        return can_trade_regular(state, player, multiworld, required_orbs, required_previous_trade)


def can_trade_regular(state: CollectionState,
                      player: int,
                      multiworld: MultiWorld,
                      required_orbs: int,
                      required_previous_trade: int = None) -> bool:

    accessible_orbs = can_reach_orbs(state, player, multiworld)
    if required_previous_trade:
        name_of_previous_trade = location_table[Cells.to_ap_id(required_previous_trade)]
        return (accessible_orbs >= required_orbs
                and state.can_reach(name_of_previous_trade, "Location", player=player))
    else:
        return accessible_orbs >= required_orbs


def can_trade_orbsanity(state: CollectionState,
                        player: int,
                        orb_bundle_size: int,
                        required_orbs: int,
                        required_previous_trade: int = None) -> bool:

    required_count = math.ceil(required_orbs / orb_bundle_size)
    orb_bundle_name = orb_item_table[orb_bundle_size]
    if required_previous_trade:
        name_of_previous_trade = location_table[Cells.to_ap_id(required_previous_trade)]
        return (state.has(orb_bundle_name, player, required_count)
                and state.can_reach(name_of_previous_trade, "Location", player=player))
    else:
        return state.has(orb_bundle_name, player, required_count)


def can_free_scout_flies(state: CollectionState, player: int) -> bool:
    return (state.has("Jump Dive", player)
            or (state.has("Crouch", player)
                and state.has("Crouch Uppercut", player)))


def can_fight(state: CollectionState, player: int) -> bool:
    return (state.has("Jump Dive", player)
            or state.has("Jump Kick", player)
            or state.has("Punch", player)
            or state.has("Kick", player))
