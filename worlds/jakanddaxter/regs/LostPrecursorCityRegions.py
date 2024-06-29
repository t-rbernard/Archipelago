from typing import List
from BaseClasses import CollectionState, MultiWorld
from .RegionBase import JakAndDaxterRegion
from .. import JakAndDaxterOptions
from ..Rules import can_free_scout_flies, can_fight


def build_regions(level_name: str, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int) -> List[JakAndDaxterRegion]:

    # Just the starting area.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 4)

    first_room_upper = JakAndDaxterRegion("First Chamber (Upper)", player, multiworld, level_name, 21)

    first_room_lower = JakAndDaxterRegion("First Chamber (Lower)", player, multiworld, level_name, 0)
    first_room_lower.add_fly_locations([262193], access_rule=lambda state: can_free_scout_flies(state, player))

    first_room_orb_cache = JakAndDaxterRegion("First Chamber Orb Cache", player, multiworld, level_name, 22)

    # Need jump dive to activate button, double jump to reach blue eco to unlock cache.
    first_room_orb_cache.add_cache_locations([14507], access_rule=lambda state:
                                             state.has("Jump Dive", player)
                                             and state.has("Double Jump", player))

    first_hallway = JakAndDaxterRegion("First Hallway", player, multiworld, level_name, 10)
    first_hallway.add_fly_locations([131121], access_rule=lambda state: can_free_scout_flies(state, player))

    # This entire room is accessible with floating platforms and single jump.
    second_room = JakAndDaxterRegion("Second Chamber", player, multiworld, level_name, 28)

    # These items can only be gotten with jump dive to activate a button.
    second_room.add_cell_locations([45], access_rule=lambda state: state.has("Jump Dive", player))
    second_room.add_fly_locations([49, 65585], access_rule=lambda state: state.has("Jump Dive", player))

    # This is the scout fly on the way to the pipe cell, requires normal breaking moves.
    second_room.add_fly_locations([196657], access_rule=lambda state: can_free_scout_flies(state, player))

    # This orb vent and scout fly are right next to each other, can be gotten with blue eco and the floating platforms.
    second_room.add_fly_locations([393265])
    second_room.add_cache_locations([14838])

    # Named after the cell, includes the armored lurker room.
    center_complex = JakAndDaxterRegion("Center of the Complex", player, multiworld, level_name, 17)
    center_complex.add_cell_locations([51])

    color_platforms = JakAndDaxterRegion("Color Platforms", player, multiworld, level_name, 6)
    color_platforms.add_cell_locations([44], access_rule=lambda state: can_fight(state, player))

    quick_platforms = JakAndDaxterRegion("Quick Platforms", player, multiworld, level_name, 3)

    # Jump dive to activate button.
    quick_platforms.add_cell_locations([48], access_rule=lambda state: state.has("Jump Dive", player))

    first_slide = JakAndDaxterRegion("First Slide", player, multiworld, level_name, 22)

    # Raised chamber room, includes vent room with scout fly prior to second slide.
    capsule_room = JakAndDaxterRegion("Capsule Chamber", player, multiworld, level_name, 6)

    # Use jump dive to activate button inside the capsule. Blue eco vent can ready the chamber and get the scout fly.
    capsule_room.add_cell_locations([47], access_rule=lambda state: state.has("Jump Dive", player))
    capsule_room.add_fly_locations([327729])

    second_slide = JakAndDaxterRegion("Second Slide", player, multiworld, level_name, 31)

    helix_room = JakAndDaxterRegion("Helix Chamber", player, multiworld, level_name, 30)
    helix_room.add_cell_locations([46], access_rule=lambda state:
                                  state.has("Double Jump", player)
                                  or state.has("Jump Kick", player)
                                  or (state.has("Punch", player) and state.has("Punch Uppercut", player)))
    helix_room.add_cell_locations([50], access_rule=lambda state:
                                  state.has("Double Jump", player)
                                  or can_fight(state, player))

    main_area.connect(first_room_upper)                   # Run.

    first_room_upper.connect(main_area)                   # Run.
    first_room_upper.connect(first_hallway)               # Run and jump (floating platforms).
    first_room_upper.connect(first_room_lower)            # Run and jump down.

    first_room_lower.connect(first_room_upper)            # Run and jump (floating platforms).

    # Needs some movement to reach these orbs and orb cache.
    first_room_lower.connect(first_room_orb_cache, rule=lambda state:
                             state.has("Jump Dive", player)
                             and state.has("Double Jump", player))
    first_room_orb_cache.connect(first_room_lower, rule=lambda state:
                                 state.has("Jump Dive", player)
                                 and state.has("Double Jump", player))

    first_hallway.connect(first_room_upper)                         # Run and jump down.
    first_hallway.connect(second_room)                              # Run and jump (floating platforms).

    second_room.connect(first_hallway)                              # Run and jump.
    second_room.connect(center_complex)                             # Run and jump down.

    center_complex.connect(second_room)                             # Run and jump (swim).
    center_complex.connect(color_platforms)                         # Run and jump (swim).
    center_complex.connect(quick_platforms)                         # Run and jump (swim).

    color_platforms.connect(center_complex)                         # Run and jump (swim).

    quick_platforms.connect(center_complex)                         # Run and jump (swim).
    quick_platforms.connect(first_slide)                            # Slide.

    first_slide.connect(capsule_room)                               # Slide.

    capsule_room.connect(second_slide)                              # Slide.
    capsule_room.connect(main_area, rule=lambda state:              # Chamber goes back to surface.
                         state.has("Jump Dive", player))            # (Assume one-way for sanity.)

    second_slide.connect(helix_room)                                # Slide.

    helix_room.connect(quick_platforms, rule=lambda state:          # Escape to get back to here.
                       state.has("Double Jump", player)             # Capsule is a convenient exit to the level.
                       or can_fight(state, player))

    multiworld.regions.append(main_area)
    multiworld.regions.append(first_room_upper)
    multiworld.regions.append(first_room_lower)
    multiworld.regions.append(first_room_orb_cache)
    multiworld.regions.append(first_hallway)
    multiworld.regions.append(second_room)
    multiworld.regions.append(center_complex)
    multiworld.regions.append(color_platforms)
    multiworld.regions.append(quick_platforms)
    multiworld.regions.append(first_slide)
    multiworld.regions.append(capsule_room)
    multiworld.regions.append(second_slide)
    multiworld.regions.append(helix_room)

    return [main_area]
