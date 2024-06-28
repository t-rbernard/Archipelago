from ..GameID import jak1_id

# Precursor Orbs are not necessarily given ID's by the game.

# Of the 2000 orbs (or "money") you can pick up, only 1233 are standalone ones you find in the overworld.
# We can identify them by Actor ID's, which run from 549 to 24433. Other actors reside in this range,
# so like Power Cells these are not ordered, nor contiguous, nor exclusively orbs.

# In fact, other ID's in this range belong to actors that spawn orbs when they are activated or when they die,
# like steel crates, orb caches, Spider Cave gnawers, or jumping on the Plant Boss's head. These orbs that spawn
# from parent actors DON'T have an Actor ID themselves - the parent object keeps track of how many of its orbs
# have been picked up.

# Rather than dealing with this mess, we're instead creating a single table of 2000 Locations, each representing 1 orb.
# When you pick up any orb in the game, you check the next progressive Location in the table. Each Location will have
# an access rule that requires you to have the equivalent number of orbs in the all the regions you have access to.

# We can use 2^15 to offset them from Orb Caches, because Orb Cache ID's max out at (jak1_id + 17792).
orb_offset = 32768


# These helper functions do all the math required to get information about each
# precursor orb and translate its ID between AP and OpenGOAL.
def to_ap_id(game_id: int) -> int:
    assert game_id < jak1_id, f"Attempted to convert {game_id} to an AP ID, but it already is one."
    return jak1_id + orb_offset + game_id   # Add the offsets and the orb Actor ID.


def to_game_id(ap_id: int) -> int:
    assert ap_id >= jak1_id, f"Attempted to convert {ap_id} to a Jak 1 ID, but it already is one."
    return ap_id - jak1_id - orb_offset  # Reverse process, subtract the offsets.
