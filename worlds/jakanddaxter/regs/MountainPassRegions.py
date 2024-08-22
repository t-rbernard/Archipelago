from typing import List
from BaseClasses import MultiWorld
from .RegionBase import JakAndDaxterRegion
from .. import JakAndDaxterOptions, EnableOrbsanity, JakAndDaxterWorld

from ..locs import ScoutLocations as Scouts


def build_regions(level_name: str, world: JakAndDaxterWorld, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int) -> List[JakAndDaxterRegion]:

    # This is basically just Klaww.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 0)
    main_area.add_cell_locations([86])

    race = JakAndDaxterRegion("Race", player, multiworld, level_name, 50)
    race.add_cell_locations([87])

    # All scout flies can be broken with the zoomer.
    race.add_fly_locations(Scouts.locMP_scoutTable.keys())

    shortcut = JakAndDaxterRegion("Shortcut", player, multiworld, level_name, 0)
    shortcut.add_cell_locations([110])

    main_area.connect(race)

    # You cannot go backwards from Klaww.
    race.connect(shortcut, rule=lambda state: state.has("Yellow Eco Switch", player))

    shortcut.connect(race)

    multiworld.regions.append(main_area)
    multiworld.regions.append(race)
    multiworld.regions.append(shortcut)

    # If Per-Level Orbsanity is enabled, build the special Orbsanity Region. This is a virtual region always
    # accessible to Main Area. The Locations within are automatically checked when you collect enough orbs.
    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        orbs = JakAndDaxterRegion("Orbsanity", player, multiworld, level_name)

        bundle_size = options.level_orbsanity_bundle_size.value
        bundle_count = 50 // bundle_size
        for bundle_index in range(bundle_count):
            orbs.add_orb_locations(10,
                                   bundle_index,
                                   access_rule=lambda state, bundle=bundle_index:
                                   world.count_reachable_orbs(state, level_name) >= (bundle_size * (bundle + 1)))
        multiworld.regions.append(orbs)
        main_area.connect(orbs)

    # Return race required for inter-level connections.
    return [main_area, race]
