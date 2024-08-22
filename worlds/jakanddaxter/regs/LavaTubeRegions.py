from typing import List
from BaseClasses import MultiWorld
from .RegionBase import JakAndDaxterRegion
from .. import JakAndDaxterOptions, EnableOrbsanity, JakAndDaxterWorld

from ..locs import CellLocations as Cells, ScoutLocations as Scouts


def build_regions(level_name: str, world: JakAndDaxterWorld, multiworld: MultiWorld, options: JakAndDaxterOptions, player: int) -> List[JakAndDaxterRegion]:

    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 50)

    # Everything is accessible by making contact with the zoomer.
    main_area.add_cell_locations(Cells.locLT_cellTable.keys())
    main_area.add_fly_locations(Scouts.locLT_scoutTable.keys())

    multiworld.regions.append(main_area)

    # If Per-Level Orbsanity is enabled, build the special Orbsanity Region. This is a virtual region always
    # accessible to Main Area. The Locations within are automatically checked when you collect enough orbs.
    if options.enable_orbsanity == EnableOrbsanity.option_per_level:
        orbs = JakAndDaxterRegion("Orbsanity", player, multiworld, level_name)

        bundle_size = options.level_orbsanity_bundle_size.value
        bundle_count = 50 // bundle_size
        for bundle_index in range(bundle_count):
            orbs.add_orb_locations(14,
                                   bundle_index,
                                   access_rule=lambda state, bundle=bundle_index:
                                   world.count_reachable_orbs(state, level_name) >= (bundle_size * (bundle + 1)))
        multiworld.regions.append(orbs)
        main_area.connect(orbs)

    return [main_area]
